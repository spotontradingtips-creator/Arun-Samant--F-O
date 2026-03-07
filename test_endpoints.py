import sys
import os
import requests
import json

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

from src.market_data import MStockAPI
from src.utils import setup_logging

def test_endpoints():
    api = MStockAPI()
    if not api.access_token:
        print("No access token found. Please authenticate first.")
        return

    endpoints = [
        ("Quote (Type A)", "GET", f"{api.base_url}/instruments/quote/ohlc?i=NSE:NIFTY+50"),
        ("Holdings (Type A)", "GET", f"{api.base_url}/portfolio/holdings"),
        ("Positions (Type A)", "GET", f"{api.base_url}/portfolio/positions"),
        ("Tradebook (GET)", "GET", f"{api.base_url}/orders/tradebook"),
        ("Tradebook (POST)", "POST", f"{api.base_url}/orders/tradebook"),
        ("Orderbook (GET)", "GET", f"{api.base_url}/orders/orderbook"),
        ("Orderbook (POST)", "POST", f"{api.base_url}/orders/orderbook"),
    ]

    for name, method, url in endpoints:
        print(f"\n--- Testing {name} ---")
        try:
            if method == "GET":
                resp = requests.get(url, headers=api.get_headers(), timeout=10)
            else:
                resp = requests.post(url, headers=api.get_headers(), json={}, timeout=10)
            
            print(f"Status: {resp.status_code}")
            if resp.status_code == 200:
                print("Success!")
                # print(resp.json())
            else:
                print(f"Response: {resp.text[:200]}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_endpoints()
