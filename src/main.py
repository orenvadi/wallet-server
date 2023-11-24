import uvicorn
from fastapi import FastAPI, WebSocket
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse

from auth.api import google_oauth_client
from auth.base_config import auth_backend, fastapi_users
from auth.schemas import UserCreate, UserRead, UserUpdate
from config import SECRET
from currency.services import (get_history_prices, get_history_prices_coincap,
                               get_history_prices_gecko, send_tickers)
from wallet.routers import wallet_router

app = FastAPI(title="Crypta")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/api/v1/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/api/v1/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/api/v1/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/api/v1/auth",
    tags=["auth"],
)
# User endpoints
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/api/v1/users",
    tags=["users"],
)
# Google Cloud 0auth
app.include_router(
    fastapi_users.get_oauth_router(google_oauth_client, auth_backend, SECRET),
    prefix="/auth/google",
    tags=["auth"],
)
# Coins/Currencies endpoint
# Wallet endpoint
app.include_router(
    router=wallet_router,
    prefix="/api/v1/wallet",
    tags=["wallet"],
)


@app.get("/")
async def root():
    return {"message": "main_app"}


@app.get("/api/v1/currency/get/prices/coincap")
async def get_prices_by_coincap(interval: str = "d1"):
    return get_history_prices_coincap(interval=interval)


@app.get("/api/v1/currency/get/prices/gecko")
async def get_prices_by_gecko(
    symbol: str = "bitcoin",
    vs_currency: str = "usd",
    days: str | int = "90",
    interval: str = "daily",
):
    return get_history_prices_gecko(
        symbol=symbol, vs_currency=vs_currency, days=days, interval=interval
    )


@app.websocket("/prices/")
async def websocket_endpoint(websocket: WebSocket, coin_name: str = "ALL"):
    await websocket.accept()
    await send_tickers(websocket, coin_name=coin_name)


@app.websocket("/history/?{coin_name}&{interval}")
async def websocket_endpoint(websocket: WebSocket, coin_name: str, interval: str):
    await websocket.accept()
    await get_history_prices(websocket, coin_name=coin_name, interval=interval)


@app.get("/api/v1/currency/get")
def read_root(coin_name: str):
    return HTMLResponse(
        f"""
        <!DOCTYPE html>
        <html>
            <head>
                <title>WebSocket Example</title>
            </head>
            <body>
                <h1>WebSocket Example</h1>
                <ul id='tickerList'></ul>
                <script>
                    var ws = new WebSocket(`ws://127.0.0.1:8000/prices/?coin_name={coin_name}`);
                    ws.onmessage = function(event) {{
                        var data = JSON.parse(event.data);
                        console.log(data);
                        var tickerList = document.getElementById('tickerList');
                        var listItem = document.createElement('li');
                        listItem.textContent = data;
                        tickerList.appendChild(listItem);
                    }};
                </script>
            </body>
        </html>
        """
    )


if __name__ == "__main__":
    uvicorn.run(app, port=8000, reload=True)
