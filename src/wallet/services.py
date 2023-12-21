import asyncio
import json

import requests
import websockets

from sqlalchemy import insert, update, select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import WebSocket, HTTPException
from src.database import async_session_maker
from src.config import BINANCE_WEBSOCKET_URL, CURRENCY_CACHE_TIME
from src.database import redis_client
from .schemas import WalletCreateSchema, CurrencyCreateSchema, CurrencyChangeSchema, TransactionCreateSchema
from .models import Wallet, Currency, Transaction, TRANSACTION_OPERATIONS


# Currency/Coin services
async def create_currency(currency_data: CurrencyCreateSchema, session: AsyncSession = async_session_maker()):
    async with session.begin():
        stmt = insert(Currency).values(**currency_data.model_dump())
        await session.execute(stmt)
        await session.commit()


async def set_currency(user_id: int, currency_data: CurrencyChangeSchema, session: AsyncSession = async_session_maker()):
    async with session.begin():
        wallet_id = select(Wallet.id).where(Wallet.user_id == user_id).scalar_subquery()

        stmt = update(Currency).values(**currency_data.model_dump()).where(
            (Currency.wallet_id == wallet_id) & (Currency.name == currency_data.name)
        )
        await session.execute(stmt)
        await session.commit()


async def set_balance(user_id: int, currency_data: CurrencyChangeSchema, session: AsyncSession = async_session_maker()):
    currency_data.name = "USDT"
    await set_currency(user_id=user_id, currency_data=currency_data, session=session)


# Wallet services
async def create_wallet(wallet_data: WalletCreateSchema, session: AsyncSession = async_session_maker()):
    async with session.begin():
        stmt = insert(Wallet).values(**wallet_data.model_dump())
        wallet_result = await session.execute(stmt)
        await session.commit()

        wallet_id = wallet_result.inserted_primary_key[0]
        new_wallet_data = wallet_data.model_dump()
        new_wallet_data["wallet_id"] = wallet_id

        await create_currency(currency_data=CurrencyCreateSchema(**new_wallet_data))


async def get_wallet(user_id: int, session: AsyncSession = async_session_maker()):
    async with session.begin():
        query = select(Wallet).where(Wallet.user_id == user_id)
        result = await session.execute(query)
        wallet = result.scalar_one_or_none()
    return wallet


# Transaction services
async def make_transaction(user_id: int, transaction_data: TransactionCreateSchema, session: AsyncSession = async_session_maker()):
    async with session.begin():
        if transaction_data.quantity <= 0:
            return HTTPException(status_code=400, detail={"message": f"You can't buy 0 or less {transaction_data.currency} coins"})
            # raise ValueError({"message": f"You can't buy 0 or less {transaction_data.currency} coins"})

        wallet_result = await session.execute(select(Wallet.id).where(Wallet.user_id == user_id))
        wallet_id = wallet_result.scalar()
        balance_result = await session.execute(select(Currency.quantity).where((Currency.wallet_id == wallet_id) & (Currency.name == "USDT")))
        balance = balance_result.scalar()
        data_dict = transaction_data.model_dump()
        price = data_dict.get("price")
        quantity = data_dict.get("quantity")
        transaction_type = data_dict.get("type")
        transaction_currency = data_dict.get("currency").upper()

        new_currency_data = {
            "name": transaction_currency,
            "quantity": quantity
        }

        currency_result = await session.execute(
            select(Currency.quantity).where(Currency.name == transaction_currency))
        currency_quantity = currency_result.scalar()

        if transaction_type not in TRANSACTION_OPERATIONS:
            return HTTPException(status_code=400, detail={"message": "Incorrect operation"})
            # raise ValueError({"message": "Incorrect operation"})

        if transaction_type == TRANSACTION_OPERATIONS[0]:
            if balance < price:
                return HTTPException(status_code=400, detail={"message": f"Your balance is less than {transaction_currency} coin's price"})
                # raise ValueError({"message": f"Your balance is less than {transaction_currency} coin's price"})

            balance = balance - quantity * price
            currency = await session.execute(select(Currency).where(Currency.name == transaction_currency))

            if currency.first() is not None:
                new_currency_data["quantity"] = currency_quantity + quantity
                await set_currency(user_id=user_id, currency_data=CurrencyChangeSchema(**new_currency_data))
            else:
                new_currency_data["wallet_id"] = wallet_id
                await create_currency(currency_data=CurrencyCreateSchema(**new_currency_data))

        if transaction_type == TRANSACTION_OPERATIONS[1]:
            if balance <= 0:
                return HTTPException(status_code=400, detail={f"There is not enough balance in your wallet"})
                # raise ValueError({"message": f"There is not enough balance in your wallet"})

            balance = balance + quantity * price

            if currency_quantity is None or currency_quantity <= 0:
                return HTTPException(status_code=400, detail={"message": f"You have not enough {transaction_currency} coins"})
                # raise ValueError({"message": f"You have not enough {transaction_currency} coins"})

            if currency_quantity < 0:
                return HTTPException(status_code=400, detail={"message": "You can't sell more coins than you have"})
                # raise ValueError({"message": "You can't sell more coins than you have"})

            new_currency_data["quantity"] = currency_quantity - quantity
            await set_currency(user_id=user_id, currency_data=CurrencyChangeSchema(**new_currency_data))

        new_transaction_data = transaction_data.model_dump()
        new_transaction_data["currency"] = new_transaction_data["currency"].upper()
        new_transaction_data["type"] = str(new_transaction_data["type"])
        stmt = insert(Transaction).values(wallet_id=wallet_id, **new_transaction_data)

        new_balance_data = {
            "name": "USDT",
            "quantity": balance
        }

        await session.execute(stmt)
        await session.commit()
        await set_balance(user_id=user_id, currency_data=CurrencyChangeSchema(**new_balance_data))


async def get_currency_data():
    try:
        i: int = 1
        keys = redis_client.keys("*")
        values = []
        for key in keys:
            value = redis_client.get(key)
            values.append(value)
            print(f"Iter {i}, Key: {key}, Value: {value}")
            i += 1
        return zip(keys, values)
    finally:
        redis_client.close()


# Redis
def process_json_list(json_list, coin_name):
    try:
        if coin_name.upper() == "ALL":
            for json_data in json_list:
                if "USDT" not in json_data["s"]:
                    continue
                event_time = json_data["E"]
                symbol = json_data["s"]
                key = f"{str(event_time)}_{symbol}"
                redis_client.set(key, str(json_data), ex=CURRENCY_CACHE_TIME)
        else:
            if "USDT" in json_list["s"]:
                event_time = json_list["E"]
                symbol = json_list["s"]
                key = f"{str(event_time)}_{symbol}"
                redis_client.set(key, str(json_list), ex=CURRENCY_CACHE_TIME)
    finally:
        redis_client.close()


# BinanceAPI services
async def send_tickers(websocket: WebSocket, coin_name: str = "ALL"):
    url = BINANCE_WEBSOCKET_URL

    try:
        connection_url = (
            url + "!miniTicker@arr"
            if coin_name.upper() == "ALL"
            else url + coin_name.lower() + "@miniTicker"
        )
        async with websockets.connect(uri=connection_url) as ws:
            while True:
                data = await ws.recv()
                json_list = json.loads(data)
                await asyncio.to_thread(process_json_list, json_list=json_list, coin_name=coin_name)
                await websocket.send_json(data)
                await asyncio.sleep(1)
    except Exception as e:
        print(f"Error in send_tickers: {e}")


async def get_history_prices(websocket: WebSocket, coin_name: str, interval: str):
    uri = BINANCE_WEBSOCKET_URL
    async with (websockets.connect(uri=f"{uri}{coin_name}@kline_{interval}") as ws):
        while True:
            data = await ws.recv()
            await websocket.send_json(data)
            await asyncio.sleep(1)


# OtherCryptaAPI services
def get_history_prices_coincap(interval: str = "d1"):
    url = f"https://api.coincap.io/v2/assets/bitcoin/history?interval={interval}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data['data']
    return response.status_code


def get_history_prices_gecko(symbol: str = "bitcoin", vs_currency: str = "usd",
                                days: str | int = "90", interval: str = "daily"):
    url = f'https://api.coingecko.com/api/v3/coins/{symbol}/market_chart'
    params = {
        'vs_currency': vs_currency,
        'days': days,
        'interval': interval,
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data
    return response.status_code
