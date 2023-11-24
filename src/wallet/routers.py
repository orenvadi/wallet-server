from fastapi import APIRouter, Depends
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models import User
from database import get_async_session
from wallet.models import Wallet
from wallet.schemas import (CurrencyChangeSchema, TransactionCreateSchema,
                            WalletCreateSchema)

from .services import (create_currency, get_wallet, make_transaction,
                       set_balance)

wallet_router = APIRouter()


@wallet_router.get("/get")
async def get_wallet(user_id: int, session: AsyncSession = Depends(get_async_session)):
    result = get_wallet(user_id=user_id, session=session)
    return result


@wallet_router.patch("/set/balance/")
async def set_balance(
    user_id: int,
    currency_data: CurrencyChangeSchema,
    session: AsyncSession = Depends(get_async_session),
):
    result = set_balance(user_id=user_id, currency_data=currency_data, session=session)
    return result


@wallet_router.post("/make/transaction")
async def make_transaction(
    user_id: int,
    transaction_data: TransactionCreateSchema,
    session: AsyncSession = Depends(get_async_session),
):
    result = make_transaction(
        user_id=user_id, transaction_data=transaction_data, session=session
    )
    return result


# @wallet_router.post("create/currency")
# async def create_currency(user_id: int, transaction_data: TransactionCreateSchema, session: AsyncSession = Depends(get_async_session)):
#     result = create_currency(user_id=user_id, transaction_data=transaction_data, session=session)
#     return result


# @wallet_router.post()


# @wallet_router.get("/get")
# async def get_wallet(session: AsyncSession = Depends(get_async_session)):
#     query = select(Wallet).where(Wallet.user_id == User.id)
#     result = await session.execute(query)
#     return result.one()


# @wallet_router.post("/create")
# async def create_wallet(wallet_data: WalletCreateSchema, session: AsyncSession = Depends(get_async_session)):
#     stmt = insert(Wallet).values(**wallet_data.dict())
#     await session.execute(stmt)
#     return {"HTTP STATUS 201 CREATED": "Wallet was successfully created"}
