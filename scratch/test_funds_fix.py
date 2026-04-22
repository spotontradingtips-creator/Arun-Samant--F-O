
import sys
import os
import json
import logging

# Add src to path
sys.path.insert(0, os.getcwd())

from src.market_data import MStockAPI
from src.trading_config import config

# Setup a dummy logger for console visibility
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("rich")

def test_funds():
    print("\n--- Testing Hardened get_funds ---")
    api = MStockAPI()
    
    # Check if session is valid
    if not api.ensure_session_is_valid():
        print("Session invalid. Re-authenticating might be needed.")
        return

    funds = api.get_funds()
    if funds is not None:
        print(f"SUCCESS: Successfully fetched funds: Rs {funds:,.2f}")
    else:
        print("FAILED: get_funds returned None. Check logs for raw response.")

if __name__ == "__main__":
    test_funds()
