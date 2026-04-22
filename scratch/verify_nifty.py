import logging
import os
import sys
from dotenv import load_dotenv

# Add root to path
root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, root)

from src.market_data import MStockAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_nifty_quote():
    print("\n--- NIFTY SYMBOL VERIFICATION TEST ---")
    api = MStockAPI()
    
    if not api.ensure_session_is_valid():
        print("FAIL: Could not establish valid session.")
        return

    symbols_to_test = [
        "NIFTY", "NIFTY 50", "NSE:NIFTY", 
        "1|26000", "NIFTY_50", "NSE:NIFTY_50", "Nifty_50", "NSE:Nifty_50"
    ]
    
    for sym in symbols_to_test:
        print(f"\nProbing Symbol: {sym}...")
        quote = api.get_quote(sym, "NSE")
        if quote:
            print(f"SUCCESS! {sym} price: {quote.get('last_price')}")
        else:
            print(f"FAILED: {sym} returned no data.")

    print("\n--- PRE-FLIGHT CONNECTION CHECK ---")
    api.validate_connection()

if __name__ == "__main__":
    test_nifty_quote()
