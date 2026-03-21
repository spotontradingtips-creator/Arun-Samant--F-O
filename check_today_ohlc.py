import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

def check_today_ohlc():
    ticker = "^BSESN"
    print(f"Fetching yfinance data for {ticker}...")
    df = yf.download(ticker, period="1d", interval="1m", progress=False)
    
    if not df.empty:
        # Resolve MultiIndex if present
        close_series = df['Close'].iloc[:, 0] if isinstance(df['Close'], pd.DataFrame) else df['Close']
        open_series = df['Open'].iloc[:, 0] if isinstance(df['Open'], pd.DataFrame) else df['Open']
        
        print(f"yfinance Today's Open: {open_series.iloc[0]:.2f}")
        print(f"yfinance Last Close: {close_series.iloc[-1]:.2f}")
    else:
        print("yfinance returned no data for today.")

if __name__ == "__main__":
    check_today_ohlc()
