
import requests
import os
import json
from dotenv import load_dotenv

def test_mstock_symbols():
    load_dotenv(override=True)
    api_key = os.getenv('API_KEY')
    
    # Needs a valid access token from credentials.json
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

    test_symbols = [
        "NSE:NIFTY",
        "NSE:Nifty 50",
        "NSE:NIFTY50",
        "1|26000",
        "NSE:NIFTY BANK",
        "NSE:NIFTYBANK",
        "1|26009",
        "BSE:SENSEX",
        "2|51"
    ]

    for sym in test_symbols:
        params = {"i": sym}
        try:
            resp = requests.get(base_url, headers=headers, params=params, timeout=10)
            print(f"Symbol: {sym:20} | Status: {resp.status_code}")
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == "success":
                    price = data.get("data", {}).get(sym, {}).get("last_price")
                    print(f"  [SUCCESS] Price: {price}")
                else:
                    print(f"  [ERROR] {data.get('message')}")
            else:
                print(f"  [FAIL] Body: {resp.text}")
        except Exception as e:
            print(f"  [EXC] {e}")

if __name__ == "__main__":
    test_mstock_symbols()
