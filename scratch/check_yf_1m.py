
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

def check_yf_1m():
    ticker = "^NSEI"
    print(f"Requesting YFinance for {ticker} (1m)...")
    df = yf.download(ticker, period="1d", interval="1m", progress=False)
    
    if not df.empty:
        print(f"Total bars: {len(df)}")
        print(df.tail(5))
        print(f"Timezone: {df.index.tz}")
    else:
        print("YFinance 1m returned empty dataframe")

if __name__ == "__main__":
    check_yf_1m()
