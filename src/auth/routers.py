from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth.api import google_oauth_client
from auth.base_config import auth_backend, fastapi_users
from auth.schemas import (LoginSchema, RoleCreateSchema, UserCreate, UserRead,
                          UserUpdate)
from auth.services import create__default__role, create__role, get__role, login
from config import SECRET
from database import get_async_session

auth_router = APIRouter()

auth_router.include_router(
    fastapi_users.get_auth_router(auth_backend),
)
auth_router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
)
auth_router.include_router(
    fastapi_users.get_reset_password_router(),
)
auth_router.include_router(
    fastapi_users.get_verify_router(UserRead),
)
# Google Cloud 0auth
auth_router.include_router(
    fastapi_users.get_oauth_router(
        google_oauth_client,
        auth_backend,
        SECRET,
        is_verified_by_default=True,
        associate_by_email=True,
    ),
)
# User endpoints
auth_router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
)


@auth_router.post("/login/custom")
async def login_custom(
    login_data: LoginSchema, session: AsyncSession = Depends(get_async_session)
):
    email = login_data.email
    password = login_data.password
    return await login(email=email, password=password, session=session)


@auth_router.post("/create/role")
async def create_role(
    user_id: int,
    role_data: RoleCreateSchema,
    session: AsyncSession = Depends(get_async_session),
):
    return await create__role(user_id=user_id, role_data=role_data, session=session)


@auth_router.post("/get/role")
async def get_role(user_id: int, session: AsyncSession = Depends(get_async_session)):
    return await get__role(user_id=user_id, session=session)


# Only for DEVs
@auth_router.post("/create/default_role")
async def create_default_role(session: AsyncSession = Depends(get_async_session)):
    return await create__default__role(session=session)
