import uvicorn
from fastapi import FastAPI

from auth.auth import auth_app
from auth.middelware_auth import middelware_app

app = FastAPI(title="Wallet")
app.mount("/api/v1", auth_app)
app.mount("/auth", middelware_app)


@app.get("/")
async def root():
    return {"message": "main_app"}


if __name__ == "__main__":
    uvicorn.run(app, port=8080, reload=True)
