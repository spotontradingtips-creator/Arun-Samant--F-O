import json
import os

filepath = "nfo_master.csv"
if not os.path.exists(filepath):
    print("Master file not found.")
else:
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            data = json.load(f)
            
        futures = []
        for item in data:
            if item.get('symbol') == "SENSEX" and item.get('instrumenttype') == "FUTIDX":
                futures.append({
                    "expiry": item.get('expiry'),
                    "token": item.get('token'),
                    "name": item.get('name')
                })
        
        futures.sort(key=lambda x: x['expiry'])
        for f in futures:
            print(f"EXPIRY: {f['expiry']} | TOKEN: {f['token']} | NAME: {f['name']}")
            
    except Exception as e:
        print(f"Error: {e}")
