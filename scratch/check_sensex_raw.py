
import requests
import json
import os
from datetime import datetime
import pytz
from urllib.parse import quote
from dotenv import load_dotenv

load_dotenv(override=True)

def check_sensex_raw():
    api_key = os.getenv('API_KEY')
    with open("credentials.json", "r") as f:
        creds = json.load(f)
        access_token = creds.get("mstock", {}).get("access_token")

    base_url = "https://api.mstock.trade/openapi/typea"
    headers = {"Authorization": f"token {api_key}:{access_token}", "X-Mirae-Version": "1"}

    ist = pytz.timezone("Asia/Kolkata")
    now_ist = datetime.now(ist)
    from_dt = now_ist.replace(hour=9, minute=15, second=0, microsecond=0)
    
    # SENSEX (BSE Token 51)
    url = f"{base_url}/instruments/historical/BSE/51/15minute?from={quote(from_dt.strftime('%Y-%m-%d %H:%M:%S'))}&to={quote(now_ist.strftime('%Y-%m-%d %H:%M:%S'))}"
    
    print(f"Requesting SENSEX 15m: {url}")
    resp = requests.get(url, headers=headers)
    print(f"Status Code: {resp.status_code}")
    print(f"Response: {resp.text}")

if __name__ == "__main__":
    check_sensex_raw()
