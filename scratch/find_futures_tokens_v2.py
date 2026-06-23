import json

def find_futures():
    with open("nfo_master.csv", "r", encoding='utf-8') as f:
        try:
            data = json.load(f)
            futures = []
            for item in data:
                symbol = item.get('symbol')
                name = item.get('name', '')
                instrument = item.get('instrumenttype', '')
                expiry = item.get('expiry', '')
                
                if symbol in ["NIFTY", "BANKNIFTY", "SENSEX"] and instrument == "FUTIDX":
                    futures.append(item)
                    
            # Sort by symbol and expiry
            futures.sort(key=lambda x: (x['symbol'], x['expiry']))
            
            for f in futures:
                print(f"Symbol: {f['symbol']} | Expiry: {f['expiry']} | Token: {f['token']} | Name: {f['name']}")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    find_futures()
