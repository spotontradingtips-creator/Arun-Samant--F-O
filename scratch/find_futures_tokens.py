
import requests
import json
import os
from datetime import datetime
import pytz
from urllib.parse import quote
from dotenv import load_dotenv

load_dotenv(override=True)

def check_futures_raw():
    api_key = os.getenv('API_KEY')
    with open("credentials.json", "r") as f:
        creds = json.load(f)
        access_token = creds.get("mstock", {}).get("access_token")

    base_url = "https://api.mstock.trade/openapi/typea"
    headers = {"Authorization": f"token {api_key}:{access_token}", "X-Mirae-Version": "1"}

    ist = pytz.timezone("Asia/Kolkata")
    now_ist = datetime.now(ist)
    from_dt = now_ist.replace(hour=9, minute=15, second=0, microsecond=0)
    
    # NIFTY APR FUT (Need to find token from master or guess common ones)
    # Usually Nifty Fut tokens are in the 35000-70000 range.
    # I'll just check if I can find them in the symbol master first.
    pass

if __name__ == "__main__":
    # Actually, I'll just try several common tokens for Nifty Fut.
    # Or better, I'll use the findstr command again.
    import subprocess
    cmd = 'findstr /i "NIFTY" nfo_master.csv | findstr /i "FUT"'
    # No, I'll just use a python script to search the file.
    with open("nfo_master.csv", "r") as f:
        count = 0
        for line in f:
            if "NIFTY" in line and "FUT" in line:
                print(line.strip())
                count += 1
                if count > 5: break
