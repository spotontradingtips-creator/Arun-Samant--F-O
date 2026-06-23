import requests
import json
import os
from dotenv import load_dotenv
import time

def verify_direct_quotes():
    load_dotenv(override=True)
    with open('credentials.json', 'r') as f:
        token = json.load(f)['mstock']['access_token']
        
    headers = {'X-Mirae-Version': '1', 'Authorization': f'Bearer {token}'}
    symbols = ["NSE:Nifty 50", "NSE:NIFTY BANK", "BSE:SENSEX"]
    
    print(f"{'INDEX':<15} | {'LATENCY':<10} | {'STATUS'}")
    print("-" * 45)
    
    for s in symbols:
        start = time.time()
        try:
            url = f"https://api.mstock.trade/openapi/typea/marketdata/v1/quotes?i={s}"
            r = requests.get(url, headers=headers)
            latency = (time.time() - start) * 1000
            
            if r.status_code == 200:
                print(f"{s:<15} | {latency:>7.1f}ms | [DIRECT] Success")
            else:
                print(f"{s:<15} | {latency:>7.1f}ms | [FAILED] HTTP {r.status_code}")
        except Exception as e:
            print(f"{s:<15} | ERROR      | {e}")

if __name__ == "__main__":
    verify_direct_quotes()
