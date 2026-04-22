import json
import os
import sys
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.getcwd())

def prober_audit():
    load_dotenv()
    api_key = os.getenv('API_KEY')
    base_url_typea = "https://api.mstock.trade/openapi/typea"
    
    try:
        with open("credentials.json", "r") as f:
            creds = json.load(f)
            access_token = creds.get("mstock", {}).get("access_token")
    except:
        print("ERROR: credentials.json not found.")
        return

    headers = {
        "Authorization": f"token {api_key}:{access_token}",
        "X-Mirae-Version": "1"
    }

    print("--- STARTING DEEP API PROBE (APRIL 1 - APRIL 10) ---")
    
    # Dates
    from_date = "2026-04-01"
    to_date = "2026-04-10"
    
    # Potential Historical Endpoints
    endpoints = [
        ("LEDGER", f"{base_url_typea}/reports/ledger?from={from_date}&to={to_date}"),
        ("TRADES_ALT", f"{base_url_typea}/reports/tradelist?from={from_date}&to={to_date}"),
        ("ORDERS_HIST", f"{base_url_typea}/orders/historical?from={from_date}&to={to_date}"),
        ("FUNDS", f"{base_url_typea}/portfolio/funds"),
        ("NET_POSITIONS", f"{base_url_typea}/portfolio/positions")
    ]

    for name, url in endpoints:
        print(f"PROBING {name}...")
        try:
            resp = requests.get(url, headers=headers, timeout=20)
            print(f"  Result: {resp.status_code}")
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == "success":
                    result_data = data.get("data", [])
                    print(f"  SUCCESS! Found items: {len(result_data) if isinstance(result_data, list) else 'Dict response'}")
                    # Print first item for verification
                    if result_data:
                        print(f"  Sample: {str(result_data)[:200]}...")
                    
                    # Special handling for FUNDS to see ROI baseline
                    if name == "FUNDS":
                         print(f"  FUNDS DATA: {data.get('data')}")
                         
                else:
                    print(f"  API Error Message: {data.get('message', 'No message')}")
        except Exception as e:
            print(f"  Connection Error: {e}")

if __name__ == '__main__':
    prober_audit()
