from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import requests
import sqlite3
import jwt
import datetime
from typing import Dict

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_db_connection():
    conn = sqlite3.connect("wallet.db")
    conn.execute("""
    CREATE TABLE IF NOT EXISTS wallet (
        user TEXT,
        currency TEXT,
        amount REAL,
        PRIMARY KEY (user, currency)
    )""")
    conn.commit()
    return conn

# Authentication Models and Token Generation
class Token(BaseModel):
    access_token: str
    token_type: str

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@app.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = form_data.username
    token = create_access_token({"sub": user})
    return {"access_token": token, "token_type": "bearer"}

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# NBP Exchange Rate Fetching
def get_exchange_rates() -> Dict[str, float]:
    response = requests.get("https://api.nbp.pl/api/exchangerates/tables/C?format=json")
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Error fetching exchange rates")
    rates = {entry["code"]: entry["ask"] for entry in response.json()[0]["rates"]}
    return rates

# Wallet Management
@app.get("/wallet")
def get_wallet(user: str = Depends(get_current_user)):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT currency, amount FROM wallet WHERE user = ?", (user,))
    wallet = {row[0]: row[1] for row in cur.fetchall()}
    conn.close()
    
    exchange_rates = get_exchange_rates()
    pln_values = {currency: round(wallet[currency] * exchange_rates.get(currency, 0), 2) for currency in wallet}
    total_pln = round(sum(pln_values.values()), 2)
    
    return {"wallet": wallet, "pln_values": pln_values, "total_pln": total_pln}

@app.post("/wallet/add/{currency}/{amount}")
def add_currency(currency: str, amount: float, user: str = Depends(get_current_user)):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO wallet (user, currency, amount) VALUES (?, ?, ?) ON CONFLICT(user, currency) DO UPDATE SET amount = amount + ?", (user, currency, amount, amount))
    conn.commit()
    conn.close()
    return {"message": f"Added {amount} {currency} to wallet"}

@app.post("/wallet/sub/{currency}/{amount}")
def subtract_currency(currency: str, amount: float, user: str = Depends(get_current_user)):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT amount FROM wallet WHERE user = ? AND currency = ?", (user, currency))
    row = cur.fetchone()
    if not row or row[0] < amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    cur.execute("UPDATE wallet SET amount = amount - ? WHERE user = ? AND currency = ?", (amount, user, currency))
    conn.commit()
    conn.close()
    return {"message": f"Subtracted {amount} {currency} from wallet"}
