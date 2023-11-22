from datetime import datetime
from typing import List

from fastapi_users_db_sqlalchemy import (SQLAlchemyBaseOAuthAccountTable,
                                         SQLAlchemyBaseUserTable)
from sqlalchemy import (JSON, TIMESTAMP, Boolean, Column, ForeignKey, Integer,
                        String)
from sqlalchemy.orm import Mapped, relationship

from database import Base

metadata = Base.metadata


class OAuthAccount(SQLAlchemyBaseOAuthAccountTable[int], Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    oauth_name = Column(String, index=True, nullable=False)
    access_token = Column(String, nullable=False)
    expires_at = Column(Integer, nullable=True)
    refresh_token = Column(Integer, nullable=True)
    account_id = Column(String, index=True, nullable=False)
    account_email = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="oauth_accounts")


class Role(Base):
    __tablename__ = "role"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    name = Column("name", String, nullable=False)
    permissions = Column("permissions", JSON)
    user = relationship("User", back_populates="role", uselist=False)


class User(SQLAlchemyBaseUserTable[int], Base):
    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False)
    registered_at = Column(TIMESTAMP, default=datetime.utcnow)
    role_id = Column(Integer, ForeignKey("role.id"))
    hashed_password: str = Column(String(length=1024), nullable=False)
    is_active: bool = Column(Boolean, default=True, nullable=False)
    is_superuser: bool = Column(Boolean, default=False, nullable=False)
    is_verified: bool = Column(Boolean, default=False, nullable=False)
    oauth_accounts: Mapped[List[OAuthAccount]] = relationship(
        "OAuthAccount", lazy="joined"
    )
    role = relationship("Role", back_populates="user")
    wallet = relationship("Wallet", back_populates="user", uselist=False)
