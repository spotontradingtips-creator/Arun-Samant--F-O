import os
import sys
import pandas as pd
import yfinance as yf
import pytz
from datetime import datetime

# Add src to path
sys.path.append(os.getcwd())
from src.indicators import TechnicalIndicators
from src.market_data import MStockAPI

def check_rsi():
    api = MStockAPI()
    indices = {
        'NIFTY': '^NSEI',
        'BANKNIFTY': '^NSEBANK',
        'SENSEX': '^BSESN'
    }
    
    print("\n--- RSI NATIVE 60D AUDIT ---")
    for name, ticker in indices.items():
        try:
            # 1. Fetch 60 Days Native (Verified to have 1400+ bars)
            df = yf.download(ticker, period='60d', interval='15m', progress=False)
            if df.empty:
                print(f"{name}: No data found.")
                continue
                
            # Clean headers
            df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
            df = df.rename(columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close'})
            
            # TZ conversion
            if df.index.tz is None:
                df.index = df.index.tz_localize("UTC").tz_convert("Asia/Kolkata")
            else:
                df.index = df.index.tz_convert("Asia/Kolkata")
            
            # 2. Apply Monday Synthesis (Anti-Ghosting)
            df = api._ensure_continuity(ticker, df)
            
            # 3. Calculate RSI
            rsi_series = TechnicalIndicators.calculate_rsi(df['close'])
            current_rsi = rsi_series.iloc[-1]
            
            print(f"{name}: {current_rsi:.2f} (Native 60d)")
            
        except Exception as e:
            print(f"{name} Error: {e}")

if __name__ == "__main__":
    check_rsi()
