import sys
import os
import pandas as pd
import numpy as np
import logging

# Setup path
sys.path.append(os.getcwd())

from src.market_data import MStockAPI
from src.indicators import TechnicalIndicators
from src.trading_config import TradingConfig

# Mock logger
logging.basicConfig(level=logging.INFO)

def diag():
    api = MStockAPI()
    ti = TechnicalIndicators()
    
    indices = [
        ("NIFTY", "NSE", "26000"),
        ("BANKNIFTY", "NSE", "26009"),
        ("SENSEX", "BSE", "1")
    ]
    
    print(f"{'Index':<15} | {'Bot Daily ADX':<15} | {'Bot 15m RSI':<15} | {'LTP':<10}")
    print("-" * 65)
    
    for symbol, exch, token in indices:
        try:
            # 1. Fetch Daily (matching main.py:76)
            d_df = api.get_historical_data(symbol, exch, token, "day", days=250)
            if d_df is not None:
                d_df['ADX'], _, _ = ti.calculate_adx(d_df['high'], d_df['low'], d_df['close'])
                daily_adx = d_df['ADX'].iloc[-1]
            else:
                daily_adx = -1
                
            # 2. Fetch Intraday (matching main.py:85)
            i_df, _ = api.get_hybrid_history(symbol, exch, token, "15minute", days=10)
            if i_df is not None:
                i_df['RSI'] = ti.calculate_rsi(i_df['close'])
                rsi_val = i_df['RSI'].iloc[-1]
                ltp = i_df['close'].iloc[-1]
            else:
                rsi_val = -1
                ltp = -1
                
            print(f"{symbol:<15} | {daily_adx:<15.2f} | {rsi_val:<15.2f} | {ltp:<10.2f}")
        except Exception as e:
            print(f"Error {symbol}: {e}")

if __name__ == "__main__":
    diag()
