
import os
import sys
import pandas as pd
from datetime import datetime
import pytz

# Add src to path
sys.path.append(os.path.abspath('src'))

from market_data import MStockAPI
from config import Config

def audit():
    config = Config()
    api = MStockAPI()
    
    indices = ['NIFTY', 'BANKNIFTY', 'SENSEX']
    
    print(f"\n{'='*60}")
    print(f"FnO BOT CONDITION AUDIT - {datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    for symbol in indices:
        print(f"--- [{symbol}] ---")
        
        # 1. Fetch Data
        try:
            # Daily Data for ADX
            daily_data = api.get_historical_data(symbol, 'day')
            if daily_data.empty:
                print(f"❌ Error: No Daily Data for {symbol}")
                continue
            
            # Intraday Data for RSI and MACD
            intraday_data = api.get_historical_data(symbol, '15minute')
            if intraday_data.empty:
                print(f"❌ Error: No Intraday Data for {symbol}")
                continue
            
            # Indicators
            daily_adx = daily_data['ADX'].iloc[-1]
            current_rsi = intraday_data['RSI'].iloc[-1]
            
            # MACD Jump (CE side)
            hist = intraday_data['MACD_Hist']
            current_hist = hist.iloc[-1]
            prev_hist = hist.iloc[-2] if len(hist) > 1 else 0
            jump = current_hist - prev_hist
            
            # Thresholds
            adx_min = config.adx_daily_min
            rsi_min, rsi_max = config.rsi_min, config.rsi_max
            jump_min = config.momentum_jump
            
            # Status
            adx_ok = "PASS" if daily_adx > adx_min else "FAIL"
            rsi_ok = "PASS" if rsi_min <= current_rsi <= rsi_max else "FAIL"
            jump_ok = "PASS" if jump >= jump_min else "FAIL"
            
            print(f"1. Daily ADX ({adx_min}+): {daily_adx:.2f} -> {adx_ok}")
            print(f"2. 15m RSI ({rsi_min}-{rsi_max}): {current_rsi:.2f} -> {rsi_ok}")
            print(f"3. MACD Jump (+{jump_min}): {jump:+.2f} -> {jump_ok} (Hist: {current_hist:.2f})")
            
            if adx_ok == "PASS" and rsi_ok == "PASS" and jump_ok == "PASS":
                print(f"✅ ALL HARD GATES MET for {symbol} CE!")
            else:
                print(f"⏳ Waiting for momentum sync...")
            
        except Exception as e:
            print(f"❌ Error auditing {symbol}: {e}")
        print("-" * 30)

if __name__ == "__main__":
    audit()
