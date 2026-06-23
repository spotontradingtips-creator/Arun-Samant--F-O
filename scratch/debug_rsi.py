import sys
import os
import pandas as pd
from datetime import datetime
import pytz

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.market_data import MStockAPI
from src.indicators import TechnicalIndicators
from src.utils import now_ist, setup_logging

logger = setup_logging("logs/debug_rsi.log")

def debug_nifty_rsi():
    api = MStockAPI()
    symbol = "NIFTY"
    exchange = "NSE"
    token = "26000"
    
    print(f"--- FETCHING DATA FOR {symbol} ---")
    
    # 1. Fetch quote
    quote = api.get_quote(symbol, exchange)
    spot = quote.get('last_price', 0) if quote else 0
    print(f"Live Spot: {spot}")
    
    # 2. Fetch history
    # This will trigger our new recovery logic (1m resampling -> 15m)
    i_df, stable = api.get_hybrid_history(symbol, exchange, token, "15minute", days=10)
    
    if i_df is None or i_df.empty:
        print("Error: No data fetched.")
        return

    print(f"Latest bar in raw df: {i_df.index[-1]}")
    print(f"Close of latest bar: {i_df.iloc[-1]['close']}")
    
    # 3. Simulate Leading Edge Synthesis (from main.py)
    ist = now_ist()
    b_s = ist.replace(minute=ist.minute - ist.minute % 15, second=0, microsecond=0)
    
    print(f"Targeting partial bar at: {b_s}")
    
    if b_s not in i_df.index:
        last_close = i_df.iloc[-1]['close']
        new_bar = pd.DataFrame([{
            'open': last_close, 'high': max(last_close, spot), 
            'low': min(last_close, spot), 'close': spot
        }], index=[b_s])
        i_df = pd.concat([i_df, new_bar])
        print("Synthesized new leading bar.")
    else:
        i_df.loc[b_s, 'close'] = spot
        print("Updated existing leading bar.")

    # 4. Calculate RSI
    i_df['RSI'] = TechnicalIndicators.calculate_rsi(i_df['close'])
    
    # 5. Output
    print("\n--- RECENT 15M BARS ---")
    print(i_df.tail(10)[['open', 'high', 'low', 'close', 'RSI']])
    
    latest_rsi = i_df.iloc[-1]['RSI']
    print(f"\nFINAL CALCULATED 15-MINUTE RSI: {latest_rsi:.2f}")
    
    if 50 <= latest_rsi <= 55:
        print("SUCCESS: RSI matches user's expectation (~52).")
    elif latest_rsi > 65:
        print("FAILURE: RSI is still stale (Friday data bias).")
    else:
        print("NOTE: RSI is adjusted but not in 50-55 range. Check market conditions.")

if __name__ == "__main__":
    debug_nifty_rsi()
