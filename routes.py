# routes.py
from flask import Flask, request, jsonify
from utils import create_token, token_required, get_exchange_rates, update_wallet, get_wallet
from models import users_db

app = Flask(__name__)
app.config.from_object("config.Config")

@app.route('/login', methods=['POST'])
def login():
    """Login route to generate JWT token."""
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    # Check username and password (simplified)
    user = next((user_id for user_id, user_data in users_db.items() if user_data["username"] == username and user_data["password"] == password), None)
    if user:
        token = create_token(user)
        return jsonify({"token": token})
    return jsonify({"message": "Invalid credentials"}), 401

@app.route('/wallet', methods=['GET'])
@token_required
def view_wallet(user_id):
    """Get the current wallet and its PLN equivalent."""
    wallet = get_wallet(user_id)
    if not wallet:
        return jsonify({"message": "Wallet is empty."}), 400

    rates = get_exchange_rates()
    total_pln = 0
    wallet_pln = {}

    for currency, amount in wallet.items():
        if currency in rates:
            pln_value = amount * float(rates[currency])
            wallet_pln[currency] = {"amount": amount, "pln_value": pln_value}
            total_pln += pln_value

    return jsonify({"wallet": wallet_pln, "total_pln": total_pln})

@app.route('/wallet/add/<currency>/<float:amount>', methods=['POST'])
@token_required
def add_currency(user_id, currency, amount):
    """Add currency to the wallet."""
    update_wallet(user_id, currency, amount)
    return jsonify({"message": f"{amount} {currency} added to wallet."})

@app.route('/wallet/sub/<currency>/<float:amount>', methods=['POST'])
@token_required
def subtract_currency(user_id, currency, amount):
    """Subtract currency from the wallet."""
    wallet = get_wallet(user_id)
    if currency not in wallet or wallet[currency] < amount:
        return jsonify({"message": "Insufficient funds."}), 400
    update_wallet(user_id, currency, -amount)
    return jsonify({"message": f"{amount} {currency} subtracted from wallet."})

if __name__ == "__main__":
    app.run(debug=True)
