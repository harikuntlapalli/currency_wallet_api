from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.services import WalletService
from app.utils import get_current_user
from app.models import Wallet
from pydantic import BaseModel

router = APIRouter()

class WalletEntry(BaseModel):
    currency: str
    amount: float

@router.get("/")
def get_wallet(user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    return WalletService.get_wallet(db)

@router.post("/add")
def add_currency(entry: WalletEntry, user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    WalletService.add_currency(db, entry.currency, entry.amount)
    return {"message": f"Added {entry.amount} {entry.currency.upper()} to wallet"}

@router.post("/sub")
def subtract_currency(entry: WalletEntry, user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    success = WalletService.subtract_currency(db, entry.currency, entry.amount)
    if not success:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    return {"message": f"Subtracted {entry.amount} {entry.currency.upper()} from wallet"}
