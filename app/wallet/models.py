from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

metadata = Base.metadata


class Wallet(Base):
    __tablename__ = "wallet"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", onupdate="NO ACTION", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow())

    user = relationship("User", back_populates="wallets")
    currency = relationship("Currency", back_populates="wallets")
    transaction = relationship("Transaction", back_populates="wallets")


class Transaction(Base):
    __tablename__ = "transaction"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    wallet_id: Mapped[int] = mapped_column(
        ForeignKey("wallet.id", onupdate="NO ACTION", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    quantity: Mapped[int] = mapped_column(default=0, nullable=False)
    bought_price: Mapped[int] = mapped_column()
    executed_at: Mapped[datetime] = mapped_column(default=datetime.now())

    wallet = relationship("Wallet", back_populates="transactions")


class Currency(Base):
    __tablename__ = "currency"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    wallet_id: Mapped[int] = mapped_column(
        ForeignKey("wallet.id", onupdate="NO ACTION", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    quantity: Mapped[int] = mapped_column(default=0, nullable=False)

    wallet = relationship("Wallet", back_populates="currencies")
