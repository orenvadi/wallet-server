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
    name: str = "USDT"
    quantity: int = 100000


class CurrencyReadSchema(BaseModel):
    name: str
    quantity: int


class CurrencyChangeSchema(BaseModel):
    name: str = "USDT"
    quantity: int


class TransactionCreateSchema(BaseModel):
    currency: str
    quantity: int
    price: int
    type: str
