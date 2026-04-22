
import pandas as pd
from datetime import datetime
import json
import os

# Manual indicator check using the logs/data files if available
def check_status():
    print("FnO Bot Status Audit (Manual Check)")
    print("-" * 30)
    
    # Check if we have recent log entries for ADX
    log_file = "logs/trading_bot_20260421.log"
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            lines = f.readlines()[-100:] # Last 100 lines
            for line in lines:
                if "Daily ADX=" in line:
                    print(f"Detected Log ADX: {line.strip()}")
    
    # Check current config
    if os.path.exists('config.json'):
        with open('config.json', 'r') as f:
            config = json.load(f)
            print(f"Config ADX Min: {config.get('adx_daily_min', 30)}")
            print(f"Config RSI Range: {config.get('rsi_min', 30)}-{config.get('rsi_max', 70)}")

if __name__ == "__main__":
    check_status()
