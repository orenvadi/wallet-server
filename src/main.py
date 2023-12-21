import uvicorn
from fastapi import FastAPI, WebSocket
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse

from auth.routers import auth_router
from wallet.routers import wallet_router
from wallet.services import (get_history_prices, get_history_prices_coincap,
                             get_history_prices_gecko, send_tickers)

app = FastAPI(title="Crypta")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth endpoint
app.include_router(router=auth_router, prefix="/api/v1/auth", tags=["Auth"])

# Wallet endpoint
app.include_router(
    router=wallet_router,
    prefix="/api/v1/wallet",
    tags=["Wallet"],
)


@app.get("/Hello", tags=["Hello"])
async def root():
    return {"message": "Hello it's main_app"}


@app.get("/api/v1/currency/get/prices/coincap", tags=["API"])
async def get_prices_by_coincap(interval: str = "d1"):
    return get_history_prices_coincap(interval=interval)


@app.get("/api/v1/currency/get/prices/gecko", tags=["API"])
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
    await send_tickers(websocket=websocket, coin_name=coin_name)


@app.websocket("/history/")
async def websocket_endpoint(websocket: WebSocket, coin_name: str, interval: str):
    await websocket.accept()
    await get_history_prices(
        websocket=websocket, coin_name=coin_name, interval=interval
    )


@app.get("/api/v1/currency/get/", tags=["API"])
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
                    var ws = new WebSocket(`ws://127.0.0.1:8080/prices/?coin_name={coin_name}`);
                    ws.onmessage = function(event) {{
                        var data = JSON.parse(event.data);
                        console.log(data);
                        var tickerList = document.getElementById('tickerList');
                        var listItem = document.createElement('li');
                        listItem.textContent = data;
                        tickerList.appendChild(listItem);
                    }};
                    
                    window.addEventListener('beforeunload', function() {{
                        ws.close();
                    }});
                </script>
            </body>
        </html>
        """
    )


if __name__ == "__main__":
    uvicorn.run(app, port=8080, reload=True)
