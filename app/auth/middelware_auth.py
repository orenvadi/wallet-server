from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import JSONResponse

from config import SECRET

middelware_app = FastAPI()

SECRET_KEY = SECRET or None

if SECRET_KEY is None:
    raise "Missing SECRET_KEY"
middelware_app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)


@middelware_app.get("/")
def test():
    return JSONResponse({"message": "auth_app"})
