import os

from dotenv import load_dotenv

load_dotenv()

DB_HOST = "monorail.proxy.rlwy.net"
DB_PORT = "19582"
DB_NAME = "railway"
DB_USER = "postgres"
DB_PASS = "2Ac6acabE-1fg*4DfgaD**5cg3gGadd6"

SECRET = "fldsmkfjnduyeiwofncmxvdbjdew392tu9g8fdfdsdjk"

GOOGLE_CLIENT_ID = (
    "380176176992-s29p01n145j0t9rmnk3o7ctfkmsb4l0c.apps.googleusercontent.com"
)

GOOGLE_CLIENT_SECRET = "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"


CURRENCY_URL = "https://api.binance.com/api/v3/ticker/price"
USD_PRICES_URI = "wss://ws.coincap.io/prices"
BINANCE_WEBSOCKET_URL = "wss://stream.binance.com:9443/ws/"
