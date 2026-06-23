import sys
import os
import pandas as pd
import time
from datetime import datetime
import pytz

# Setup path
sys.path.append(os.getcwd())

from src.market_data import MStockAPI
from src.indicators import TechnicalIndicators
from src.trading_config import TradingConfig

def run_check():
    api = MStockAPI()
    ti = TechnicalIndicators()
    config = TradingConfig() # Load defaults or from file if preferred
    
    # Try to load config from JSON if it exists
    try:
        import json
        with open("config.json", "r") as f:
            c_data = json.load(f)
            # Simple override for specific fields we need
            config.adx_intraday_min = c_data.get("indicators", {}).get("adx_intraday_min", 22.0)
            config.rsi_pe_min = c_data.get("indicators", {}).get("rsi_pe_min", 35.0)
            config.rsi_pe_max = c_data.get("indicators", {}).get("rsi_pe_max", 70.0)
    except: pass

    indices = [
        ("NIFTY", "NSE", "26000"),
        ("BANKNIFTY", "NSE", "26009"),
        ("SENSEX", "BSE", "1")
    ]
    
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)
    
    print("=" * 70)
    print(f" LIVE RULE AUDIT - {now.strftime('%Y-%m-%d %H:%M:%S')} IST")
    print("=" * 70)
    print(f"{'Index':<12} | {'Price':<10} | {'RSI (15m)':<10} | {'15m ADX':<10} | {'Status'}")
    print("-" * 70)
    
    for name, exch, token in indices:
        try:
            # Intraday RSI, ADX & Price
            i_df, _ = api.get_hybrid_history(name, exch, token, "15minute", days=10)
            i_df['RSI'] = ti.calculate_rsi(i_df['close'])
            i_df['ADX'], _, _ = ti.calculate_adx(i_df['high'], i_df['low'], i_df['close'])
            
            rsi_val = i_df['RSI'].iloc[-1]
            intraday_adx = i_df['ADX'].iloc[-1]
            ltp = i_df['close'].iloc[-1]
            
            # Evaluate Status
            adx_ok = intraday_adx >= config.adx_intraday_min
            rsi_pe_ok = config.rsi_pe_min <= rsi_val <= config.rsi_pe_max
            
            status = "PASS" if (adx_ok and rsi_pe_ok) else "WAIT (Logic Gate)"
            if not adx_ok: status += " [ADX Low]"
            if not rsi_pe_ok: status += " [RSI Climax]"
            
            print(f"{name:<12} | {ltp:<10.2f} | {rsi_val:<10.2f} | {intraday_adx:<10.2f} | {status}")
            
        except Exception as e:
            print(f"{name:<12} | ERROR: {str(e)[:40]}")

    print("-" * 70)
    print(f"Rules: 15m ADX >= {config.adx_intraday_min} | RSI PE Range: {config.rsi_pe_min}-{config.rsi_pe_max}")
    print("=" * 70)

if __name__ == "__main__":
    run_check()
