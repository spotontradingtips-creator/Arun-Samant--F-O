import os
import sys
from datetime import datetime
import pandas as pd
import pytz

# Add root to path
sys.path.append(os.getcwd())

from src.trading_config import TradingConfig
from src.market_data import MStockAPI
from src.indicators import TechnicalIndicators

def debug_rsi():
    config = TradingConfig()
    api = MStockAPI()
    
    symbol = "NIFTY"
    print(f"\n--- RSI PRECISION DEBUG: {symbol} ---")
    
    # Get Hybrid History (This should now trigger Anti-Ghosting)
    df, is_calibrated = api.get_hybrid_history(symbol, "NSE", "26000", "15minute")
    
    print(f"Total Bars: {len(df)}")
    
    # Check Monday Coverage
    mon = df[df.index.date == pd.Timestamp('2026-04-20').date()]
    print(f"Monday Bars: {len(mon)}")
    if not mon.empty:
         print(mon.head(2))
         print(mon.tail(2))
    else:
         print("[CRITICAL] Monday is STILL missing!")
         
    # Check Friday Coverage
    fri = df[df.index.date == pd.Timestamp('2026-04-17').date()]
    print(f"Friday Bars: {len(fri)}")
    
    # Calculate RSI
    rsi_vals = TechnicalIndicators.calculate_rsi(df['close'], period=14)
    print(f"Live RSI (Last 3):")
    print(rsi_vals.tail(3))
    
    print("\n[VERIFICATION] TradingView Value: 63.36")
    if abs(rsi_vals.iloc[-1] - 63.36) > 2:
         print(f"[FAIL] Discrepancy too large: {rsi_vals.iloc[-1]:.2f}")
    else:
         print(f"[PASS] RSI Aligned: {rsi_vals.iloc[-1]:.2f}")

if __name__ == "__main__":
    debug_rsi()
