from fastapi import FastAPI
from app.routes import auth, wallet

app = FastAPI()

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(wallet.router, prefix="/wallet", tags=["Wallet"])
