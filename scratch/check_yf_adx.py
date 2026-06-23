import sys
import os
sys.path.insert(0, os.getcwd())
import yfinance as yf
from src.indicators import TechnicalIndicators
import pandas as pd

def check_yf_ground_truth():
    print("--- YFINANCE NIFTY GROUND TRUTH ---")
    ticker = "^NSEI"
    df = yf.download(ticker, period="1y", interval="1d")
    
    if df.empty:
        print("Failed to fetch YFinance data")
        return

    print(f"Data Points: {len(df)}")
    print(f"Latest Bar Date: {df.index[-1]}")
    print(f"Latest Bar Close: {df['Close'].iloc[-1].item():.2f}")
    
    # Calculate ADX
    # Note: YFinance returns a MultiIndex if one ticker, or just columns. 
    # To be safe, flatten columns.
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    adx, _, _ = TechnicalIndicators.calculate_adx(df['High'], df['Low'], df['Close'])
    
    print(f"Latest ADX (including live): {adx.iloc[-1]:.2f}")
    print(f"ADX (Yesterday's Close): {adx.iloc[-2]:.2f}")

if __name__ == "__main__":
    check_yf_ground_truth()
