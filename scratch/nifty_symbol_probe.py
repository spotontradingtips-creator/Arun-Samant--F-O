import requests
import json
import os
from dotenv import load_dotenv

def test_nifty_symbols():
    load_dotenv(override=True)
    
    try:
        with open('credentials.json', 'r') as f:
            creds = json.load(f)
            token = creds.get('mstock', {}).get('access_token')
    except Exception as e:
        print(f"Error reading token: {e}")
        return

    if not token:
        print("No access token found.")
        return

    headers = {
        'X-Mirae-Version': '1',
        'Authorization': f'Bearer {token}'
    }

    # Test NIFTY variations + others for comparison
    tests = [
        {"exch": "NSE", "sym": "NIFTY 50"},
        {"exch": "NSE", "sym": "Nifty 50"},
        {"exch": "NSE", "sym": "NIFTY"},
        {"exch": "NSE", "sym": "NIFTY50"},
        {"exch": "NSE", "sym": "NIFTY_50"},
        {"exch": "NSE", "sym": "26000"}, # Token check
        {"exch": "NSE", "sym": "NIFTY BANK"},
        {"exch": "NSE", "sym": "26009"}, # BN Token check
        {"exch": "BSE", "sym": "SENSEX"},
        {"exch": "BSE", "sym": "51"},     # Sensex Token check
        {"exch": "NSE", "sym": "INDIA VIX"}
    ]

    print(f"{'INDEX':<15} | {'STATUS':<7} | {'RESULT'}")
    print("-" * 50)

    for test in tests:
        exch = test["exch"]
        sym = test["sym"]
        # Symbol-based URL
        url = f"https://api.mstock.trade/openapi/typea/marketdata/v1/quotes?i={exch}:{sym}"
        try:
            r = requests.get(url, headers=headers)
            res_json = r.json()
            status = res_json.get("status", "error")
            price = res_json.get("data", {}).get(sym, {}).get("last_price", "N/A")
            print(f"{exch}:{sym:<10} | {r.status_code:<7} | Status: {status}, Price: {price}")
        except Exception as e:
            print(f"{exch}:{sym:<10} | ERROR   | {e}")

if __name__ == "__main__":
    test_nifty_symbols()
