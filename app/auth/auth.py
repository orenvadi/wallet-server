from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from auth.api import google_oauth_client
from auth.base_config import auth_backend, fastapi_users
from auth.schemas import UserCreate, UserRead, UserUpdate
from config import SECRET
from currency.routers import currency_router
from wallet.routers import wallet_router

auth_app = FastAPI(title="auth")
auth_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# login signup
auth_app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/api/v1/auth", tags=["auth"]
)
auth_app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/api/v1/auth",
    tags=["auth"],
)
auth_app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/api/v1/auth",
    tags=["auth"],
)
auth_app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/api/v1/auth",
    tags=["auth"],
)
# User endpoints
auth_app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/api/v1/users",
    tags=["users"],
)

# Google Cloud 0auth
auth_app.include_router(
    fastapi_users.get_oauth_router(google_oauth_client, auth_backend, SECRET),
    prefix="/auth/google",
    tags=["auth"],
)

auth_app.include_router(
    router=currency_router,
    prefix="/currency",
    tags=["currency"],
)

auth_app.include_router(
    router=wallet_router,
    prefix="/wallet",
    tags=["wallet"],
)
