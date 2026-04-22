
import sys
import os
import logging

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.market_data import MStockAPI

# Setup logging
logging.basicConfig(level=logging.INFO)

def test_nifty_fallback():
    print("--- NIFTY FAILOVER DIAGNOSTIC ---")
    api = MStockAPI()
    
    # This should trigger get_quote -> Broker Fail -> YFinance Fallback
    print("\nAttempting to fetch NIFTY quote...")
    quote = api.get_quote("NIFTY", "NSE")
    
    if quote:
        print(f"\n[SUCCESS] Quote Received: {quote}")
        if quote.get("source") == "YFinance Fallback":
            print("[VERIFIED] Logic successfully triggered YFinance Backup Radar.")
        else:
            print("[VERIFIED] Broker Direct is working (Fallback not needed).")
    else:
        print("\n[FAILED] Quote still None. Check network/YFinance.")

if __name__ == "__main__":
    test_nifty_fallback()
