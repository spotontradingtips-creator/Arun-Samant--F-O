
import sys
import os
import json

# Add src to path
sys.path.insert(0, os.getcwd())

from src.market_data import MStockAPI

def check_quote_raw():
    api = MStockAPI()
    if not api.ensure_session_is_valid():
        print("Session invalid")
        return

    # NSE:Nifty 50 or 1|26000
    res = api.get_quote("NIFTY", "NSE")
    print(f"NIFTY Quote: {json.dumps(res, indent=2)}")

if __name__ == "__main__":
    check_quote_raw()
