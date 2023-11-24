from pydantic import BaseModel
from datetime import datetime


class WalletCreateSchema(BaseModel):
    user_id: int


class WalletReadSchema(BaseModel):
    id: int
    user: str
    balance: int
    created_time: datetime


class CurrencyCreateSchema(BaseModel):
    wallet_id: int
    name: str = "USD"
    quantity: int = 10000


class CurrencyReadSchema(BaseModel):
    name: str
    quantity: int


class CurrencyChangeSchema(BaseModel):
    name: str = "USD"
    quantity: int


class TransactionCreateSchema(BaseModel):
    currency: str
    quantity: int
    bought_price: int | None
    sold_price: int | None
