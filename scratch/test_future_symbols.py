import requests
import json
import os
import sys

# Add src to path
sys.path.insert(0, os.getcwd())

from src.market_data import MStockAPI

api = MStockAPI()
if api.ensure_session_is_valid():
    url = f"{api.base_url}/instruments/quote/ohlc"
    headers = api.get_headers()
    
    # Test 1: NIFTY Future Symbol
    sym = "NSE:Nifty 50-I"
    print(f"Testing Symbol: {sym}")
    params = {"i": sym}
    resp = requests.get(url, headers=headers, params=params)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text}")
    
    # Test 2: Another common format
    sym = "NSE:NIFTY-I"
    print(f"\nTesting Symbol: {sym}")
    params = {"i": sym}
    resp = requests.get(url, headers=headers, params=params)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text}")
