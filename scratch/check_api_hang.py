import os
import sys
import json
import logging
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.getcwd())

from src.market_data import MStockAPI
from src.utils import setup_logging

def test_api_responsiveness():
    print("Initializing API...")
    api = MStockAPI()
    
    print("Checking session validity...")
    valid = api.ensure_session_is_valid()
    print(f"Session valid: {valid}")
    
    if not valid:
        print("Session invalid. Re-authenticating might be needed.")
        return

    print("Fetching funds...")
    try:
        funds = api.get_funds(timeout=(5, 10))
        print(f"Funds: {funds}")
    except Exception as e:
        print(f"Error fetching funds: {e}")

    print("Fetching net positions...")
    try:
        positions = api.get_net_positions(timeout=(5, 10))
        print(f"Net positions: {len(positions) if positions is not None else 'None'}")
        if positions:
            print(f"Sample position: {positions[0]}")
    except Exception as e:
        print(f"Error fetching net positions: {e}")

    print("Fetching quotes for NIFTY...")
    try:
        quote = api.get_quote("NIFTY", "NSE")
        print(f"NIFTY Quote: {quote.get('last_price') if quote else 'None'}")
    except Exception as e:
        print(f"Error fetching quote: {e}")

if __name__ == "__main__":
    test_api_responsiveness()
