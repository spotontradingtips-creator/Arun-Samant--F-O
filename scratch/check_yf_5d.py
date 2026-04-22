
import yfinance as yf
import pandas as pd

def check_yf_5d():
    ticker = "^NSEI"
    print(f"Requesting YFinance for {ticker} (15m, 5d)...")
    # Using 5d instead of 1d to avoid 'delisted' glitch
    df = yf.download(ticker, period="5d", interval="15m", progress=False)
    
    if not df.empty:
        print(f"Total bars: {len(df)}")
        print("Last 10 bars:")
        print(df.tail(10))
    else:
        print("YFinance 5d returned empty dataframe")

if __name__ == "__main__":
    check_yf_5d()
