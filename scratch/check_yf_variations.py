
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

def check_yf_variations():
    tickers = ["^NSEI", "NIFTY50.NS", "NIFTY_50.NS", "NIFTY-50.NS"]
    print("Requesting YFinance Variations (15m)...")
    
    for ticker in tickers:
        print(f"\n--- {ticker} ---")
        try:
            df = yf.download(ticker, period="1d", interval="15m", progress=False)
            if not df.empty:
                print(f"Total bars: {len(df)}")
                print(df.tail(2))
            else:
                print("Empty")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    check_yf_variations()
