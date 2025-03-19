from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Float
from app.config import Config

Base = Config.Base

class Wallet(Base):
    __tablename__ = "wallet"

    id = Column(Integer, primary_key=True, index=True)
    currency = Column(String, unique=True, index=True)
    amount = Column(Float, default=0.0)


class User(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class WalletEntry(BaseModel):
    currency: str
    amount: float
