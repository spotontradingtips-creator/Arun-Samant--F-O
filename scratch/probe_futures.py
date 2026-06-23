
import os
import sys
import requests
import json
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.market_data import MStockAPI

def probe_futures():
    api = MStockAPI()
    symbols = [
        "NSE:NIFTY26APRFUT",
        "NSE:NIFTY-I",
        "NSE:NIFTY 26APR26 FUT",
        "NSE:NIFTY APR FUT",
        "BSE:SENSEX26APRFUT",
        "BSE:SENSEX-I"
    ]
    
    print("\nPROBING FUTURE SYMBOLS FOR VWAP...")
    for sym in symbols:
        try:
            url = f"{api.base_url}/instruments/quote/ohlc"
            params = {"i": sym}
            resp = requests.get(url, headers=api.get_headers(), params=params, timeout=10)
            print(f"Symbol: {sym:25} | Status: {resp.status_code} | Body: {resp.text[:100]}")
        except Exception as e:
            print(f"Symbol: {sym:25} | Error: {e}")

if __name__ == "__main__":
    probe_futures()
