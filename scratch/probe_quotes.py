
import requests
import json
import os
from dotenv import load_dotenv

def test_quotes():
    load_dotenv(override=True)
    api_key = os.getenv('API_KEY')
    with open("credentials.json", "r") as f:
        creds = json.load(f)
    access_token = creds.get("mstock", {}).get("access_token")
    
    headers = {
        "Authorization": f"token {api_key}:{access_token}",
        "X-Mirae-Version": "1"
    }
    base_url = "https://api.mstock.trade/openapi/typea/instruments/quote/ohlc"
    
    test_symbols = [
        "NSE:NIFTY 50",
        "NSE:26000",
        "NSE:NIFTY BANK",
        "NSE:26009",
        "BSE:SENSEX",
        "BSE:51",
        "NSE:INDIA VIX"
    ]
    
    for sym in test_symbols:
        params = {"i": sym}
        try:
            resp = requests.get(base_url, headers=headers, params=params, timeout=10)
            print(f"Testing {sym}: status {resp.status_code}")
            if resp.status_code == 200:
                print(f"  Result: {resp.text[:100]}...")
            else:
                print(f"  Error: {resp.text}")
        except Exception as e:
            print(f"  Exception for {sym}: {e}")

if __name__ == "__main__":
    test_quotes()
