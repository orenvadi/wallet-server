from fastapi import APIRouter, WebSocket
from starlette.responses import HTMLResponse

from .services import send_tickers

currency_router = APIRouter()


# Middlewares should be fixed

# @currency_router.websocket("/prices/")
# async def websocket_endpoint(websocket: WebSocket, coin_name: str = "ALL"):
#     await websocket.accept()
#     await send_tickers(websocket, coin_name=coin_name)
#
#
# @currency_router.get("/currency/{coin_name}")
# def read_root(coin_name: str = "ALL"):
#     return HTMLResponse(
#         f"""
#         <!DOCTYPE html>
#         <html>
#             <head>
#                 <title>WebSocket Example</title>
#             </head>
#             <body>
#                 <h1>WebSocket Example</h1>
#                 <ul id='tickerList'></ul>
#                 <script>
#                     var ws = new WebSocket(`ws://127.0.0.1:8000/prices/?coin_name={coin_name}`);
#                     ws.onmessage = function(event) {{
#                         var data = JSON.parse(event.data);
#                         console.log('received data', data);
#
#                         var tickerList = document.getElementById('tickerList');
#
#                         var listItem = document.createElement('li');
#                         listItem.textContent = "data: " + data;
#                         tickerList.appendChild(listItem);
#                     }};
#                 </script>
#             </body>
#         </html>
#         """
#     )
