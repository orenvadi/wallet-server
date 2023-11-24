from sqlalchemy import and_, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from database import async_session_maker, get_async_session

from .models import Currency, Transaction, Wallet
from .schemas import (CurrencyChangeSchema, CurrencyCreateSchema,
                      TransactionCreateSchema, WalletCreateSchema)


async def create_currency(
    currency_data: CurrencyCreateSchema, session: AsyncSession = async_session_maker()
):
    stmt = insert(Currency).values(**currency_data.dict())
    await session.execute(stmt)
    await session.commit()
    await session.close()


async def set_currency(
    user_id: int,
    currency_data: CurrencyChangeSchema,
    session: AsyncSession = async_session_maker(),
):
    subquery = select([Wallet.id]).where(Wallet.user_id == user_id).scalar_subquery()

    stmt = (
        update(Currency)
        .values(**currency_data.dict().pop("name"))
        .where((Currency.wallet_id == subquery) & (Currency.name == currency_data.name))
    )
    await session.execute(stmt)
    await session.commit()
    await session.close()


async def create_wallet(
    wallet_data: WalletCreateSchema, session: AsyncSession = async_session_maker()
):
    stmt = insert(Wallet).values(**wallet_data.dict())
    wallet_result = await session.execute(stmt)
    await session.commit()
    await session.close()

    wallet_id = wallet_result.inserted_primary_key[0]

    default_currency_data = {"wallet_id": wallet_id, "name": "USD", "quantity": 10000}

    await create_currency(currency_data=CurrencyCreateSchema(**default_currency_data))


async def get_wallet(user_id: int, session: AsyncSession = async_session_maker()):
    query = select(Wallet).where(Wallet.user_id == user_id)
    await session.execute(query)


async def set_balance(
    user_id: int,
    currency_data: CurrencyChangeSchema,
    session: AsyncSession = async_session_maker(),
):
    subquery = select([Wallet.id]).where(Wallet.user_id == user_id).scalar_subquery()

    stmt = (
        update(Currency)
        .values(**currency_data.dict().pop("name"))
        .where((Currency.wallet_id == subquery) & (Currency.name == "USD"))
    )
    await session.execute(stmt)
    await session.commit()
    await session.close()


async def make_transaction(
    user_id: int,
    transaction_data: TransactionCreateSchema,
    session: AsyncSession = async_session_maker(),
):
    balance = await session.execute(
        select([Currency.quantity]).where(
            and_(Wallet.user_id == user_id, Wallet.currency.name == "USD")
        )
    )
    data_dict = transaction_data.dict()

    bought_price = data_dict.get("bought_price")
    sold_price = data_dict.get("sold_price")

    if sold_price and bought_price:
        raise ValueError({"error": "You are not able to buy and sell at the same time"})

    if bought_price:
        if balance.scalar() < bought_price:
            raise ValueError(
                {"error": "Your balance is less than the crypto currency price"}
            )
        balance = balance.scalar() - bought_price
        currency = await session.execute(
            select(Currency).where(Currency.name == transaction_data.currency)
        )

        if not currency:
            wallet_id = await session.execute(
                select([Wallet.id]).where(Wallet.user_id == user_id)
            )
            new_currency_data = {
                "wallet_id": wallet_id.scalar(),
                "name": transaction_data.currency,
                "quantity": transaction_data.quantity,
            }
            await create_currency(
                currency_data=CurrencyCreateSchema(**new_currency_data)
            )
        if currency:
            new_currency_data = {
                "name": transaction_data.currency,
                "quantity": transaction_data.quantity,
            }
            await set_currency(
                user_id=user_id, currency_data=CurrencyChangeSchema(**new_currency_data)
            )

    if sold_price:
        if balance.scalar() <= 0:
            raise ValueError({"error": "There is no these coins in your wallet"})
        balance = balance.scalar() + sold_price
        currency_quantity = await session.execute(
            select(Currency.quantity).where(Currency.name == transaction_data.currency)
        )

        if not currency_quantity or currency_quantity.scalar() <= 0:
            raise ValueError(
                {"error": f"You have no {transaction_data.currency} coins"}
            )

        currency_quantity = currency_quantity.scalar() - transaction_data.quantity
        if currency_quantity < 0:
            raise ValueError({"error": "You can't sell more coins than you have"})

        new_currency_data = {
            "name": transaction_data.currency,
            "quantity": currency_quantity,
        }
        await set_currency(
            user_id=user_id, currency_data=CurrencyChangeSchema(**new_currency_data)
        )

    stmt = insert(Transaction).values(user_id=user_id, **transaction_data.dict())

    new_balance_data = {"name": "USD", "quantity": balance}

    await session.execute(stmt)
    await session.commit()
    await session.close()
    await set_balance(
        user_id=user_id, currency_data=CurrencyChangeSchema(**new_balance_data)
    )
