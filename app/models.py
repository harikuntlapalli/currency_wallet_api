
from collections import defaultdict

# In-memory user data (for simplicity)
users_db = {
    1: {"username": "john", "password": "password123"}  # Dummy user data
}

wallets_db = defaultdict(dict)  # Dictionary for storing user wallets by user_id

# In-memory database for storing the wallet composition
def get_wallet(user_id):
    """Retrieve the wallet for the user."""
    return wallets_db.get(user_id, {})

def update_wallet(user_id, currency, amount):
    """Update the wallet with a given amount of currency."""
    wallet = get_wallet(user_id)
    if currency in wallet:
        wallet[currency] += amount
    else:
        wallet[currency] = amount
    wallets_db[user_id] = wallet
