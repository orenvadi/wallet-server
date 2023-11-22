from fastapi import Depends
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session

from .models import Currency, Wallet
from .schemas import CurrencyCreateSchema, WalletCreateSchema


async def create_currency(
    currency_data: CurrencyCreateSchema,
    session: AsyncSession = Depends(get_async_session),
):
    stmt = insert(Currency).values(**currency_data.dict())
    await session.execute(stmt)


async def create_wallet(
    wallet_data: WalletCreateSchema, session: AsyncSession = Depends(get_async_session)
):
    stmt = insert(Wallet).values(**wallet_data.dict())
    wallet_result = await session.execute(stmt)
    wallet_id = wallet_result.inserted_primary_key[0]

    default_currency_data = {"wallet_id": wallet_id, "name": "USD", "quantity": 10000}

    await create_currency(
        currency_data=CurrencyCreateSchema(**default_currency_data), session=session
    )


async def set_balance():
    pass
