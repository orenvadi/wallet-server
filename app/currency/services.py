import asyncio
import json

import requests
import websockets
from fastapi import WebSocket

from config import BINANCE_PRICES_URI


async def send_tickers(websocket: WebSocket, coin_name: str = "ALL"):
    uri = BINANCE_PRICES_URI
    async with (
        websockets.connect(
            uri=uri + "!miniTicker@arr"
            if coin_name.upper() == "ALL"
            else uri + coin_name.lower() + "@miniTicker"
        ) as ws
    ):
        while True:
            data = await ws.recv()
            await websocket.send_json(data)
            await asyncio.sleep(1)


def get_history_prices_coincap(interval: str = "d1"):
    url = f"https://api.coincap.io/v2/assets/bitcoin/history?interval={interval}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data["data"]
    return response.status_code


def get_history_prices_gecko(
    symbol: str = "bitcoin",
    vs_currency: str = "usd",
    days: str | int = "90",
    interval: str = "daily",
):
    url = f"https://api.coingecko.com/api/v3/coins/{symbol}/market_chart"
    params = {
        "vs_currency": vs_currency,
        "days": days,
        "interval": interval,
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data
    return response.status_code
