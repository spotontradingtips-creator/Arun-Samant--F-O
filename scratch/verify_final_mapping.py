
import requests
import os
import json
from dotenv import load_dotenv
import logging

# Set up logging to match the bot's style
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_mapping_logic():
    load_dotenv(override=True)
    api_key = os.getenv('API_KEY')
    
    try:
        with open("credentials.json", "r") as f:
            creds = json.load(f)
            access_token = creds.get("mstock", {}).get("access_token")
    except:
        print("Credentials not found")
        return

    base_url = "https://api.mstock.trade/openapi/typea/instruments/quote/ohlc"
    headers = {
        "X-Mirae-Version": "1",
        "Authorization": f"token {api_key}:{access_token}"
    }

    # Simulation of the mapping logic in MStockAPI.get_quote
    broker_mapping = {
        "NIFTY": "Nifty 50",
        "BANKNIFTY": "NIFTY BANK",
        "NIFTY50": "Nifty 50",
        "NIFTY 50": "Nifty 50",
        "NIFTY BANK": "NIFTY BANK",
        "SENSEX": "SENSEX",
        "INDIA VIX": "India VIX"
    }

    test_inputs = ["NIFTY", "BANKNIFTY", "SENSEX"]
    exchange_map = {"NIFTY": "NSE", "BANKNIFTY": "NSE", "SENSEX": "BSE"}

    for symbol in test_inputs:
        exchange = exchange_map[symbol]
        symbol_key = symbol.upper()
        mapped_symbol = broker_mapping.get(symbol_key, symbol)
        
        full_symbol = f"{exchange.upper()}:{mapped_symbol}"
        
        print(f"\nInput: {symbol} -> Mapped to: {full_symbol}")
        
        params = {"i": full_symbol}
        try:
            resp = requests.get(base_url, headers=headers, params=params, timeout=10)
            print(f"  Status: {resp.status_code}")
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == "success":
                    price = data.get("data", {}).get(full_symbol, {}).get("last_price")
                    print(f"  [SUCCESS] {full_symbol} Price: {price}")
                else:
                    print(f"  [ERROR] {data.get('message')}")
            else:
                print(f"  [FAIL] Body: {resp.text}")
        except Exception as e:
            print(f"  [EXC] {e}")

if __name__ == "__main__":
    test_mapping_logic()
