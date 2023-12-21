from typing import AsyncGenerator

from redis import StrictRedis
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base

from config import (DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER, RS_HOST,
                    RS_PORT)

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
Base: DeclarativeMeta = declarative_base()


engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


redis_client = StrictRedis(
    host=RS_HOST, port=RS_PORT, db=0, encoding="utf-8", decode_responses=True
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
