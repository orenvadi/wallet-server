from datetime import datetime
from typing import List

from fastapi_users_db_sqlalchemy import (SQLAlchemyBaseOAuthAccountTable,
                                         SQLAlchemyBaseUserTable)
from sqlalchemy import (JSON, TIMESTAMP, Boolean, Column, ForeignKey, Integer,
                        MetaData, String, Table)
from sqlalchemy.orm import Mapped, relationship

from database import Base

metadata = MetaData()
role = Table(
    "role",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False),
    Column("permissions", JSON),
)

user = Table(
    "user",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String, nullable=False),
    Column("registered_at", TIMESTAMP, default=datetime.utcnow),
    Column("role_id", Integer, ForeignKey(role.c.id)),
    Column("hashed_password", String, nullable=False),
    Column("is_active", Boolean, default=True, nullable=False),
    Column("is_superuser", Boolean, default=False, nullable=False),
    Column("is_verified", Boolean, default=False, nullable=False),
)

OauthAccount = Table(
    "oauth_account",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey(user.c.id)),
    Column("oauth_name", String, nullable=False),
    Column("access_token", String, nullable=False),
    Column("expires_at", Integer, nullable=True),
    Column("refresh_token", Integer, nullable=True),
    Column("account_id", String, nullable=False),
    Column("account_email", String, nullable=False),
)


class OAuthAccount(SQLAlchemyBaseOAuthAccountTable[int], Base):
    id = Column(Integer, primary_key=True)
    oauth_name = Column(String, index=True, nullable=False)
    access_token = Column(String, nullable=False)
    expires_at = Column(Integer, nullable=True)
    refresh_token = Column(Integer, nullable=True)
    account_id = Column(String, index=True, nullable=False)
    account_email = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="oauth_accounts")


class User(SQLAlchemyBaseUserTable[int], Base):
    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False)
    registered_at = Column(TIMESTAMP, default=datetime.utcnow)
    role_id = Column(Integer, ForeignKey(role.c.id))
    hashed_password: str = Column(String(length=1024), nullable=False)
    is_active: bool = Column(Boolean, default=True, nullable=False)
    is_superuser: bool = Column(Boolean, default=False, nullable=False)
    is_verified: bool = Column(Boolean, default=False, nullable=False)
    oauth_accounts: Mapped[List[OAuthAccount]] = relationship(
        "OAuthAccount", lazy="joined"
    )
