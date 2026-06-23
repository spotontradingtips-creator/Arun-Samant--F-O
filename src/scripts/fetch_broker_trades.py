
import json
import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import pandas as pd

def fetch_trades():
    load_dotenv()
    api_key = os.getenv('API_KEY')
    
    try:
        with open("credentials.json", "r") as f:
            creds = json.load(f)
            access_token = creds.get("mstock", {}).get("access_token")
    except:
        print("Error: credentials.json not found or invalid.")
        return

    headers = {
        "Authorization": f"token {api_key}:{access_token}",
        "X-Mirae-Version": "1"
    }

    # Target endpoints to probe for long-term history (Type B)
    to_date = datetime.now().strftime("%Y-%m-%d")
    from_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
    
    endpoints = [
        ("Type B Trade History", f"https://api.mstock.trade/openapi/typeb/instruments/historical/NSE/64860/15minute?from=2026-02-23%2009:15:00&to=2026-02-23%2015:30:00", "GET"),
        ("Type B Holdings", f"https://api.mstock.trade/openapi/typeb/portfolio/holdings", "GET"),
        ("Type B Positions", f"https://api.mstock.trade/openapi/typeb/portfolio/positions", "GET"),
        ("Type A Ledger (Fallback)", f"https://api.mstock.trade/openapi/typea/reports/ledger?from={from_date}&to={to_date}", "GET")
    ]

    print(f"Probing Type B Endpoints...")
    for name, url, method in endpoints:
        try:
            # Type B often uses Bearer token or different header
            # Let's try current headers first
            resp = requests.get(url, headers=headers, timeout=15)
            print(f"{name}: {resp.status_code}")
            if resp.status_code == 200:
                print(f" -> Found data!")
        except Exception as e:
            print(f"{name} failed: {e}")

if __name__ == "__main__":
    fetch_trades()
