import sys
import os
import pandas as pd

# Add project root to path
sys.path.insert(0, os.getcwd())

from src.market_data import MStockAPI
from src.indicators import TechnicalIndicators

def investigate_nifty_adx():
    print("--- NIFTY DAILY ADX DEEP DIVE ---")
    api = MStockAPI()
    
    # Fetch 250 days of history
    df = api.get_historical_data("Nifty 50", "NSE", "26000", "day", days=250)
    if df is None:
        print("Failed to fetch data")
        return

    print(f"Data Points: {len(df)}")
    print(f"Latest Bar: {df.index[-1]} | Close: {df['close'].iloc[-1]}")
    
    # Calculate ADX
    adx, plus_di, minus_di = TechnicalIndicators.calculate_adx(df['high'], df['low'], df['close'])
    
    current_adx = adx.iloc[-1]
    print(f"Calculated ADX: {current_adx:.2f}")
    
    # Look at the last 5 days of ADX
    print("\nRecent ADX Trend:")
    print(adx.tail(5))

    # Potential cause: Is today's live candle included?
    # Usually ADX 14 on daily charts uses ONLY closed days.
    # If we include the "Live" day, it can skew the value.
    df_closed = df.iloc[:-1] # Remove the last (live) bar
    adx_closed, _, _ = TechnicalIndicators.calculate_adx(df_closed['high'], df_closed['low'], df_closed['close'])
    print(f"\nADX (Closed Days Only): {adx_closed.iloc[-1]:.2f}")

if __name__ == "__main__":
    investigate_nifty_adx()
