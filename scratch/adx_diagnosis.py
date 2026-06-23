
import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime
import pytz

# Add src to path
sys.path.insert(0, os.getcwd())

from src.market_data import MStockAPI
from src.indicators import TechnicalIndicators

def diag_adx():
    api = MStockAPI()
    
    indices = [
        {"name": "SENSEX", "exch": "BSE", "token": "51", "user_val": 22.63},
        {"name": "NIFTY", "exch": "NSE", "token": "26000", "user_val": 22.13},
        {"name": "BANKNIFTY", "exch": "NSE", "token": "26009", "user_val": 21.97}
    ]
    
    print(f"ADX DIAGNOSIS | Time: {datetime.now()}")
    print("-" * 80)
    
    for item in indices:
        name = item["name"]
        exch = item["exch"]
        token = item["token"]
        user_val = item["user_val"]
        
        # Test 1: Current Logic (60 days, Flat Today Bar)
        df_60 = api.get_historical_data(name, exch, token, "day", days=60)
        adx_60, _, _ = TechnicalIndicators.calculate_adx(df_60['high'], df_60['low'], df_60['close'])
        val_60 = adx_60.iloc[-1]
        
        # Test 2: Extended Logic (250 days)
        df_250 = api.get_historical_data(name, exch, token, "day", days=250)
        adx_250, _, _ = TechnicalIndicators.calculate_adx(df_250['high'], df_250['low'], df_250['close'])
        val_250 = adx_250.iloc[-1]
        
        # Test 3: Corrected OHLC Synthesis (Manual override for diag)
        # Let's get the quote and fix the last bar
        quote = api.get_quote(name, exch)
        if quote and 'ohlc' in quote:
            q_ohlc = quote['ohlc']
            df_fix = df_250.copy()
            # If the last bar is today, fix it
            ist = pytz.timezone("Asia/Kolkata")
            today = datetime.now(ist).date()
            if df_fix.index[-1].date() == today:
                df_fix.iloc[-1, df_fix.columns.get_loc('open')] = q_ohlc['open']
                df_fix.iloc[-1, df_fix.columns.get_loc('high')] = q_ohlc['high']
                df_fix.iloc[-1, df_fix.columns.get_loc('low')] = q_ohlc['low']
                df_fix.iloc[-1, df_fix.columns.get_loc('close')] = quote['last_price']
            
            adx_fix, _, _ = TechnicalIndicators.calculate_adx(df_fix['high'], df_fix['low'], df_fix['close'])
            val_fix = adx_fix.iloc[-1]
        else:
            val_fix = 0

        print(f"Index: {name}")
        print(f"  User Value (Chart): {user_val}")
        print(f"  Current Bot (60d, Flat): {val_60:.2f} (Diff: {val_60 - user_val:+.2f})")
        print(f"  Bot (250d, Flat): {val_250:.2f} (Diff: {val_250 - user_val:+.2f})")
        print(f"  Bot (250d, Fixed OHLC): {val_fix:.2f} (Diff: {val_fix - user_val:+.2f})")
        print("-" * 80)

if __name__ == "__main__":
    diag_adx()
