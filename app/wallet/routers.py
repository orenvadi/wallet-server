from fastapi import APIRouter, Depends
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models import User
from database import get_async_session
from wallet.models import Wallet
from wallet.schemas import WalletCreateSchema

wallet_router = APIRouter()


@wallet_router.get("/get")
async def get_wallet(session: AsyncSession = Depends(get_async_session)):
    query = select(Wallet).where(Wallet.user_id == User.id)
    result = await session.execute(query)
    return result.one()


@wallet_router.post("/create")
async def create_wallet(
    wallet_data: WalletCreateSchema, session: AsyncSession = Depends(get_async_session)
):
    stmt = insert(Wallet).values(**wallet_data.dict())
    await session.execute(stmt)
    return {"HTTP STATUS 201 CREATED": "Wallet was successfully created"}
