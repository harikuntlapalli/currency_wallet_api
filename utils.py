# utils.py
import jwt
import datetime
import requests
from functools import wraps
from flask import request, jsonify
from config import Config 

def create_token(user_id):
    """Create a JWT token for the user."""
    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # expires in 1 hour
    }
    return jwt.encode(payload, Config.SECRET_KEY, algorithm="HS256")

def decode_token(token):
    """Decode JWT token to get user_id."""
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
        return payload["user_id"]
    except jwt.ExpiredSignatureError:
        raise Exception("Token has expired.")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token.")

def token_required(f):
    """Decorator to protect routes requiring a valid token."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]  # Get token part from header
        if not token:
            return jsonify({"message": "Token is missing!"}), 401
        try:
            user_id = decode_token(token)
        except Exception as e:
            return jsonify({"message": str(e)}), 401
        return f(user_id, *args, **kwargs)
    return decorated_function
def get_exchange_rates():
    """Fetch current exchange rates from the NBP API."""
    response = requests.get(Config.NBP_API_URL)
    if response.status_code == 200:
        data = response.json()
        rates = {rate["currency"]: rate["rates"][0]["ask"] for rate in data[0]["rates"]}
        return rates
    return {}