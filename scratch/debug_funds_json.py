from src.market_data import MStockAPI
import requests
import json

def debug_funds():
    api = MStockAPI()
    if not api.access_token:
        print("No access token")
        return
    
    url = f"{api.base_url}/user/fundsummary"
    resp = requests.get(url, headers=api.get_headers())
    print(f"Status Code: {resp.status_code}")
    print(f"Response: {resp.text}")

if __name__ == "__main__":
    debug_funds()
