import json
import os

filepath = "nfo_master.csv"
if not os.path.exists(filepath):
    print("Master file not found.")
else:
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            data = json.load(f)
            
        print(f"Total records: {len(data)}")
        
        # Search for NIFTY and BANKNIFTY FUTIDX
        futures = []
        for item in data:
            if item.get('instrumenttype') == "FUTIDX":
                symbol = item.get('symbol')
                if symbol in ["NIFTY", "BANKNIFTY"]:
                    futures.append({
                        "symbol": symbol,
                        "expiry": item.get('expiry'),
                        "token": item.get('token'),
                        "name": item.get('name')
                    })
        
        # Sort by expiry
        futures.sort(key=lambda x: x['expiry'])
        
        for f in futures:
            print(f"SYMBOL: {f['symbol']} | EXPIRY: {f['expiry']} | TOKEN: {f['token']} | NAME: {f['name']}")
            
    except Exception as e:
        print(f"Error: {e}")
