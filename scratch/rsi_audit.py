import sys
import os
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
import pytz

# Add project root to path
sys.path.append(os.getcwd())

from src.market_data import MStockAPI
from src.indicators import TechnicalIndicators

def rsi_audit():
    print("--- RSI PRECISION AUDIT ---")
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)
    print(f"Current Time (IST): {now.strftime('%Y-%m-%d %H:%M:%S')}")
    
    api = MStockAPI()
    
    indices = [
        ("NIFTY", "NSE", "26000", "^NSEI"),
        ("BANKNIFTY", "NSE", "26009", "^NSEBANK"),
        ("SENSEX", "BSE", "51", "^BSESN")
    ]
    
    results = []
    
    for symbol, exch, token, yf_ticker in indices:
        print(f"\nAuditing {symbol}...")
        
        # 1. Fetch mStock Data (15m, 10 days)
        try:
            mstock_df = api.get_historical_data(symbol, exch, token, "15minute", days=10)
            if mstock_df is not None and not mstock_df.empty:
                mstock_rsi = TechnicalIndicators.calculate_rsi(mstock_df['close']).iloc[-1]
                mstock_last_price = mstock_df['close'].iloc[-1]
                mstock_last_time = mstock_df.index[-1]
            else:
                mstock_rsi = 0
                mstock_last_price = 0
                mstock_last_time = "N/A"
        except Exception as e:
            print(f"  mStock Error: {e}")
            mstock_rsi = 0
            mstock_last_price = 0
            mstock_last_time = "N/A"

        # 2. Fetch YFinance Data (15m, 10 days)
        try:
            yf_data = yf.download(yf_ticker, period="10d", interval="15m", progress=False)
            if not yf_data.empty:
                # Handle multi-index if yfinance v2
                yf_data.columns = [col[0] if isinstance(col, tuple) else col for col in yf_data.columns]
                yf_rsi = TechnicalIndicators.calculate_rsi(yf_data['Close']).iloc[-1]
                yf_last_price = yf_data['Close'].iloc[-1]
                yf_last_time = yf_data.index[-1].tz_convert(ist)
            else:
                yf_rsi = 0
                yf_last_price = 0
                yf_last_time = "N/A"
        except Exception as e:
            print(f"  YFinance Error: {e}")
            yf_rsi = 0
            yf_last_price = 0
            yf_last_time = "N/A"

        results.append({
            "Symbol": symbol,
            "mStock Price": f"{mstock_last_price:.2f}",
            "YF Price": f"{yf_last_price:.2f}",
            "mStock RSI": f"{mstock_rsi:.2f}",
            "YF RSI": f"{yf_rsi:.2f}",
            "Diff": f"{abs(mstock_rsi - yf_rsi):.2f}",
            "mStock Last Bar": mstock_last_time.strftime('%H:%M') if hasattr(mstock_last_time, 'strftime') else str(mstock_last_time)
        })

    # Display results as a table-like format
    print("\n" + "="*80)
    print(f"{'Symbol':<12} | {'mStock RSI':<10} | {'YF RSI':<10} | {'Diff':<6} | {'mStock Price':<12} | {'Last Bar'}")
    print("-" * 80)
    for res in results:
        print(f"{res['Symbol']:<12} | {res['mStock RSI']:<10} | {res['YF RSI']:<10} | {res['Diff']:<6} | {res['mStock Price']:<12} | {res['mStock Last Bar']}")
    print("="*80)

if __name__ == "__main__":
    rsi_audit()
