
import json
import os

def inspect_futures(filepath="nfo_master.csv"):
    if not os.path.exists(filepath):
        print("File not found")
        return
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        data = json.load(f)
        
    count = 0
    print("INSPECTING FUTIDX RECORDS:")
    for item in data:
        if item.get('instrumenttype') == "FUTIDX":
            print(json.dumps(item))
            count += 1
            if count >= 10:
                break

if __name__ == "__main__":
    inspect_futures()
