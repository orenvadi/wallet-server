import uvicorn
from fastapi import FastAPI, WebSocket
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse

from auth.auth import auth_app
from auth.middelware_auth import middleware_app
from currency.services import (get_history_prices_coincap,
                               get_history_prices_gecko, send_tickers)

app = FastAPI(title="Wallet")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/api/v1", auth_app)
app.mount("/auth", middleware_app)


@app.get("/")
async def root():
    return {"message": "main_app"}


@app.get("/get/prices/coincap")
async def get_prices_by_coincap(interval: str = "d1"):
    return get_history_prices_coincap(interval=interval)


@app.get("/get/prices/gecko")
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


@app.get("/currency")
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
