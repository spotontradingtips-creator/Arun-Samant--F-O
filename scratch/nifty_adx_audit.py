import yfinance as yf
import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.getcwd())
from src.indicators import TechnicalIndicators

def audit_nifty():
    ti = TechnicalIndicators()
    print("--- NIFTY DAILY ADX AUDIT ---")
    
    # 2 Years for stability
    df = yf.download("^NSEI", period="2y", interval="1d", progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] for col in df.columns]
    
    df['ADX'], df['+DI'], df['-DI'] = ti.calculate_adx(df['High'], df['Low'], df['Close'])
    
    print(df[['High', 'Low', 'Close', 'ADX']].tail(10))
    print(f"\nFinal ADX: {df['ADX'].iloc[-1]:.2f}")

if __name__ == "__main__":
    audit_nifty()
