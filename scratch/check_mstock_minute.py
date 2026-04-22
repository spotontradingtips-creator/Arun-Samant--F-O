
import requests
import json
import os
from datetime import datetime, timedelta
import pytz
from urllib.parse import quote
from dotenv import load_dotenv

load_dotenv(override=True)

def check_mstock_minute():
    api_key = os.getenv('API_KEY')
    api_secret = os.getenv('API_SECRET')
    
    with open("credentials.json", "r") as f:
        creds = json.load(f)
        access_token = creds.get("mstock", {}).get("access_token")

    base_url = "https://api.mstock.trade/openapi/typea"
    headers = {
        "Authorization": f"token {api_key}:{access_token}",
        "X-Mirae-Version": "1"
    }

    ist = pytz.timezone("Asia/Kolkata")
    now_ist = datetime.now(ist)
    from_dt = (now_ist - timedelta(days=0)).replace(hour=9, minute=15, second=0, microsecond=0)
    to_dt = now_ist
    
    from_encoded = quote(from_dt.strftime("%Y-%m-%d %H:%M:%S"))
    to_encoded = quote(to_dt.strftime("%Y-%m-%d %H:%M:%S"))
    
    # Check NIFTY (Token 26000) for 'minute'
    url = (
        f"{base_url}/instruments/historical/"
        f"NSE/26000/minute"
        f"?from={from_encoded}&to={to_encoded}"
    )
    
    print(f"Requesting 'minute' URL: {url}")
    resp = requests.get(url, headers=headers)
    print(f"Status Code: {resp.status_code}")
    try:
        data = resp.json()
        if data.get('status') == 'success':
            candles = data.get('data', {}).get('candles', [])
            print(f"Returned {len(candles)} 'minute' candles.")
            if candles:
                print(f"Last candle: {candles[-1]}")
        else:
            print(f"Error Message: {data.get('message')}")
    except:
        print(f"Body: {resp.text}")

if __name__ == "__main__":
    check_mstock_minute()
