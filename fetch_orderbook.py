import ccxt
import json
from datetime import datetime

def fetch_order_book():
    # Initialize Binance exchange (using public API, no keys needed for orderbook)
    exchange = ccxt.binance({
        'enableRateLimit': True,
    })

    pair = 'BTC/USDT'
    print(f"Fetching order book for {pair}...")

    try:
        # Fetch order book
        # limit=5 means we get the top 5 bids and asks
        orderbook = exchange.fetch_order_book(pair, limit=5)
        
        # Structure analysis
        print("\n=== Data Structure Analysis ===")
        print(f"Type: {type(orderbook)}")
        print(f"Keys: {orderbook.keys()}")
        
        print("\n=== Sample Data (Top 5) ===")
        print(json.dumps(orderbook, indent=2))
        
        print("\n=== Explanation ===")
        print("'bids': List of [price, amount] for buy orders, sorted by price desc")
        print("'asks': List of [price, amount] for sell orders, sorted by price asc")
        print("'timestamp': Timestamp in milliseconds")
        print("'datetime': ISO8601 datetime string")
        print("'nonce': Update id (exchange specific)")

    except Exception as e:
        print(f"Error fetching order book: {e}")

if __name__ == "__main__":
    fetch_order_book()
