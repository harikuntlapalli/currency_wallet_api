from sqlalchemy.orm import Session
from app.models import Wallet
import httpx
from app.config import Config


class WalletService:

    @staticmethod
    def fetch_exchange_rate(currency: str):
        url = f"https://api.nbp.pl/api/exchangerates/rates/C/{currency}/?format=json"
        try:
            response = httpx.get(url)
            response.raise_for_status()
            return response.json()["rates"][0]["ask"]
        except httpx.HTTPStatusError:
            return None

    @classmethod
    def get_wallet(cls, db: Session):
        wallets = db.query(Wallet).all()
        total_pln = 0
        wallet_pln = {}

        for wallet in wallets:
            rate = cls.fetch_exchange_rate(wallet.currency)
            if rate:
                wallet_pln[wallet.currency] = wallet.amount * rate
                total_pln += wallet_pln[wallet.currency]

        return {"wallet": wallet_pln, "total_pln": total_pln}

    @classmethod
    def add_currency(cls, db: Session, currency: str, amount: float):
        currency = currency.upper()
        wallet_entry = db.query(Wallet).filter(Wallet.currency == currency).first()

        if wallet_entry:
            wallet_entry.amount += amount
        else:
            wallet_entry = Wallet(currency=currency, amount=amount)
            db.add(wallet_entry)

        db.commit()
        db.refresh(wallet_entry)

    @classmethod
    def subtract_currency(cls, db: Session, currency: str, amount: float):
        currency = currency.upper()
        wallet_entry = db.query(Wallet).filter(Wallet.currency == currency).first()

        if not wallet_entry or wallet_entry.amount < amount:
            return False

        wallet_entry.amount -= amount
        db.commit()
        db.refresh(wallet_entry)
        return True
