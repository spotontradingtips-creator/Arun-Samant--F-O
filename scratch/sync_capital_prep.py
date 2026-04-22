import sys
import os
import json

# Ensure the root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from src.market_data import MStockAPI
    from src.trading_config import config
    
    api = MStockAPI()
    # Attempt to fetch balance
    balance_info = api.get_funds() # Corrected method name from src/market_data.py
    
    if balance_info and balance_info > 0:
        print(f"LIVE_BALANCE:{balance_info}")
    else:
        print("ERROR: Could not fetch balance. Check session/API.")
        
except Exception as e:
    print(f"ERROR: {e}")
