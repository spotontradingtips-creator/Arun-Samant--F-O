
import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
import pytz

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.market_data import MStockAPI
from src.trading_config import config
from src.indicators import TechnicalIndicators
from src.symbol_master import SymbolMaster

def check_status():
    api = MStockAPI()
    master = SymbolMaster() # This will trigger load_master
    
    indices = [
        ('NIFTY', 'NSE', '26000'),
        ('BANKNIFTY', 'NSE', '26009'),
        ('SENSEX', 'BSE', '51')
    ]
    
    print("\n" + "="*80)
    print(f"FnO BOT LIVE CONDITION CHECK (Stage 5 - Optimized Hunter) - {datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")
    
    # Check VIX
    try:
        vix_data = api.get_historical_data('India VIX', 'NSE', '26017', '15minute')
        if vix_data is not None and not vix_data.empty:
            vix = vix_data['close'].iloc[-1]
            vix_ok = "PASS" if vix >= config.vix_min_threshold else "FAIL"
            print(f"GLOBAL: India VIX (Min {config.vix_min_threshold}): {vix:.2f} -> {vix_ok}")
        else:
            print("GLOBAL: India VIX -> DATA EMPTY")
    except Exception as e:
        print(f"GLOBAL: India VIX -> ERROR FETCHING: {e}")
    
    print("\n" + "-"*80)
    
    for symbol, exchange, token in indices:
        print(f"SYMBOL: {symbol}")
        try:
            # 1. Intraday Data (15m ADX, RSI, MACD, VWAP)
            intraday_data, is_stable = api.get_hybrid_history(symbol, exchange, token, '15minute', 10)
            if intraday_data is not None and not intraday_data.empty:
                # Add Volume from Future Proxy for VWAP
                f_info = master.future_tokens.get(symbol)
                if f_info:
                    f_df = api.get_historical_data(symbol, f_info['exch'], f_info['token'], "15minute", days=2)
                    if f_df is not None and not f_df.empty:
                        intraday_data = intraday_data.join(f_df[['volume']], rsuffix='_fut')
                        intraday_data['volume'] = intraday_data['volume_fut'].fillna(0)
                
                adx, plus_di, minus_di = TechnicalIndicators.calculate_adx(intraday_data['high'], intraday_data['low'], intraday_data['close'])
                rsi = TechnicalIndicators.calculate_rsi(intraday_data['close'])
                macd, signal, hist = TechnicalIndicators.calculate_macd(intraday_data['close'])
                vwap = TechnicalIndicators.calculate_vwap(intraday_data)
                
                curr_adx = adx.iloc[-1]
                curr_rsi = rsi.iloc[-1]
                prev_rsi = rsi.iloc[-2] if len(rsi) > 1 else curr_rsi
                curr_hist = hist.iloc[-1]
                prev_hist = hist.iloc[-2] if len(hist) > 1 else curr_hist
                jump = curr_hist - prev_hist
                curr_vwap = vwap.iloc[-1] if not vwap.empty else 0
                spot = intraday_data['close'].iloc[-1]
                
                # Condition Checks
                adx_ok = "PASS" if curr_adx >= 23.0 else "FAIL"
                rsi_ok = "PASS" if config.rsi_min <= curr_rsi <= config.rsi_max else "FAIL"
                hist_threshold = config.get_macd_threshold(symbol)
                hist_ok = "PASS" if curr_hist >= hist_threshold else "FAIL"
                jump_ok = "PASS" if jump >= 1.0 else "FAIL"
                vwap_ok = "PASS" if (curr_vwap > 0 and spot > curr_vwap) else "FAIL"
                
                print(f"  1. 15m ADX (Min 23.0): {curr_adx:.2f} -> {adx_ok}")
                print(f"  2. RSI (Range {config.rsi_min}-{config.rsi_max}): {curr_rsi:.2f} -> {rsi_ok}")
                print(f"  3. MACD Hist (Min {hist_threshold}): {curr_hist:.2f} -> {hist_ok}")
                print(f"  4. MACD Jump (Min 1.0): {jump:+.2f} -> {jump_ok}")
                print(f"  5. VWAP Gate (Spot > VWAP): Spot={spot:.2f}, VWAP={curr_vwap:.2f} -> {vwap_ok}")
                
        except Exception as e:
            print(f"  Error: {e}")
        print("-"*80)

if __name__ == "__main__":
    check_status()
