import yfinance as yf
import pandas as pd

def check_yf():
    ticker = "^NSEI"
    df = yf.download(ticker, period="1d", interval="15m", progress=False)
    print("--- YFINANCE RAW DATA ---")
    print(df.tail())
    print("\nColumns:", df.columns)
    print("\nIndex Timezone:", df.index.tz)

if __name__ == "__main__":
    check_yf()
