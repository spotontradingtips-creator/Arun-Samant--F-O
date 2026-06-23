import requests
import json
import os
from dotenv import load_dotenv

load_dotenv(override=True)
api_key = os.getenv('API_KEY')

with open("credentials.json", "r") as f:
    creds = json.load(f)
access_token = creds.get("mstock", {}).get("access_token")

base_url = "https://api.mstock.trade/openapi/typea"
headers = {
    "Authorization": f"token {api_key}:{access_token}",
    "X-Mirae-Version": "1"
}

print(f"Token length: {len(access_token) if access_token else 0}")
url = f"{base_url}/instruments/quote/ohlc"
params = {"i": "NSE:NIFTY 50"}
resp = requests.get(url, headers=headers, params=params)

print(f"Status Code: {resp.status_code}")
print(f"Response Body: {resp.text}")
