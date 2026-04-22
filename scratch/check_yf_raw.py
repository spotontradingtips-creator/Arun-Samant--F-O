
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

def check_yf_raw():
    ticker = "^NSEI"
    print(f"Requesting YFinance for {ticker} (15m)...")
    # Using period='1d' or '2d' should get today's bars
    df = yf.download(ticker, period="2d", interval="15m", progress=False)
    
    if not df.empty:
        print(f"Total bars: {len(df)}")
        print("Last 5 bars:")
        print(df.tail(5))
        
        # Check timezone
        print(f"Timezone: {df.index.tz}")
        
    else:
        print("YFinance returned empty dataframe")

if __name__ == "__main__":
    check_yf_raw()
