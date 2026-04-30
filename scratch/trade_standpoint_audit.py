import sys
import os
import pandas as pd
from datetime import datetime
import pytz

# Add project root to path
sys.path.insert(0, os.getcwd())

from src.market_data import MStockAPI
from src.trading_config import config
from src.indicators import TechnicalIndicators
from src.utils import normalize_symbol

def audit_standpoint():
    print(f"--- TRADE STANDPOINT AUDIT ({datetime.now().strftime('%H:%M:%S')}) ---")
    api = MStockAPI()
    if not api.ensure_session_is_valid():
        print("Error: API session invalid")
        return

    # 1. Check VIX
    vix_quote = api.get_quote("INDIA VIX", "NSE")
    vix = vix_quote.get('last_price', 0) if vix_quote else 0
    print(f"VIX: {vix:.2f} (Min Required: {config.vix_min_threshold})")
    if vix < config.vix_min_threshold:
        print("CRITICAL: VIX too low. Trading likely paused across all indices.")

    indices = ["NIFTY", "BANKNIFTY", "SENSEX"]
    
    for idx in indices:
        print(f"\n--- {idx} ANALYSIS ---")
        symbol_info = config.index_rules.get(idx)
        if not symbol_info: continue
        
        token = symbol_info['token']
        exchange = symbol_info['exchange'] if 'exchange' in symbol_info else ("BSE" if idx == "SENSEX" else "NSE")
        
        # Fetch Data
        d_df = api.get_historical_data(idx, exchange, token, "day", days=250)
        i_df, stable = api.get_hybrid_history(idx, exchange, token, "15minute", days=10)
        
        if d_df is None or i_df is None:
            print(f"Data Fetch Failed for {idx}")
            continue
            
        # Indicators
        adx_series, _, _ = TechnicalIndicators.calculate_adx(d_df['high'], d_df['low'], d_df['close'])
        d_adx = adx_series.iloc[-1]
        
        i_df['MACD'], i_df['MACD_Signal'], i_df['MACD_Hist'] = TechnicalIndicators.calculate_macd(i_df['close'])
        i_df['RSI'] = TechnicalIndicators.calculate_rsi(i_df['close'])
        
        current_i = i_df.iloc[-1]
        prev_i = i_df.iloc[-2] if len(i_df) > 1 else current_i
        
        rsi = current_i['RSI']
        rsi_rising = rsi > prev_i['RSI']
        rsi_falling = rsi < prev_i['RSI']
        
        hist = current_i['MACD_Hist']
        jump = hist - prev_i['MACD_Hist']
        
        macd_bullish = current_i['MACD'] > current_i['MACD_Signal']
        macd_bearish = current_i['MACD'] < current_i['MACD_Signal']
        
        hist_threshold = config.get_macd_threshold(idx)
        
        print(f"  [DAILY] ADX: {d_adx:.2f} (Min: {config.adx_daily_min}) -> {'PASS' if d_adx > config.adx_daily_min else 'FAIL'}")
        
        # CE Standpoint
        print(f"  [CE ENTRY]")
        print(f"    RSI: {rsi:.2f} (30-70) & Rising: {rsi_rising} -> {'PASS' if (30 <= rsi <= 70 and rsi_rising) else 'FAIL'}")
        print(f"    MACD: Bullish: {macd_bullish} & Hist Jump: {jump:+.2f} (Min +2.0) & Hist Val: {hist:.2f} (Min {hist_threshold})")
        ce_pass = (30 <= rsi <= 70 and rsi_rising and macd_bullish and jump >= 2.0 and hist >= hist_threshold)
        print(f"    RESULT: {'READY' if ce_pass else 'PENDING'}")
        
        # PE Standpoint
        print(f"  [PE ENTRY]")
        print(f"    RSI: {rsi:.2f} (35-75) & Falling: {rsi_falling} -> {'PASS' if (35 <= rsi <= 75 and rsi_falling) else 'FAIL'}")
        print(f"    MACD: Bearish: {macd_bearish} & Hist Jump: {jump:+.2f} (Min -2.0) & Hist Val: {hist:.2f} (Max -{hist_threshold})")
        pe_pass = (35 <= rsi <= 75 and rsi_falling and macd_bearish and jump <= -2.0 and hist <= -hist_threshold)
        print(f"    RESULT: {'READY' if pe_pass else 'PENDING'}")

if __name__ == "__main__":
    audit_standpoint()
