import sys
import os
import pandas as pd
from datetime import datetime
import pytz

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.market_data import MStockAPI

def debug_nifty_gap():
    api = MStockAPI()
    symbol = "NIFTY"
    exchange = "NSE"
    token = "26000"
    
    print(f"\n--- DEBUGGING {symbol} DATA GAP ---")
    
    # 1. Check Raw Historical (Timeframe: 15min)
    print("\n1. Calling get_historical_data(15minute)...")
    df = api.get_historical_data(symbol, exchange, token, "15minute", days=5)
    
    if df is not None and not df.empty:
        print(f"   Latest Bar Time: {df.index[-1]}")
        print(f"   Latest Close: {df.iloc[-1]['close']}")
        print(f"   Bars Count: {len(df)}")
        if df.index[-1].date() < datetime.now().date():
            print("   [!] ALERT: Data still ends on Friday!")
    else:
        print("   [!] Error: No data returned at all.")

    # 2. Check 1-minute fallback
    print("\n2. Calling get_historical_data(minute)...")
    df_m = api.get_historical_data(symbol, exchange, token, "minute", days=1)
    if df_m is not None and not df_m.empty:
        print(f"   Latest 1m Bar: {df_m.index[-1]}")
    else:
        print("   [!] 1m History also empty/stale.")

    # 3. Check YFinance Fallback
    print("\n3. Testing YFinance direct fetch...")
    import yfinance as yf
    try:
        yf_df = yf.download("^NSEI", period="1d", interval="15m", progress=False)
        if not yf_df.empty:
            print(f"   YF Latest Bar: {yf_df.index[-1]}")
    except Exception as e:
        print(f"   YF Error: {e}")

if __name__ == "__main__":
    debug_nifty_gap()
