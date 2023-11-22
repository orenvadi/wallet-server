from fastapi import FastAPI

from auth.api import google_oauth_client
from auth.base_config import auth_backend, fastapi_users
from auth.schemas import UserCreate, UserRead, UserUpdate
from config import SECRET

auth_app = FastAPI(title="auth")

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
