import sys
import traceback
import time
import pandas as pd
from datetime import datetime
import pytz

sys.path.append('c:\\Antigravity\\Arun Samant - F&O')
from src.market_data import MStockAPI
from main import get_market_data_with_indicators

def run_audit():
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] STARTING COMPREHENSIVE IP & DATA AUDIT...")
    
    try:
        api = MStockAPI()
        
        # 1. Check IP and Authentication
        print("\n--- 1. VERIFYING BROKER AUTHENTICATION & IP ---")
        is_valid = api.ensure_session_is_valid()
        if not is_valid:
            print("❌ BROKER AUTHENTICATION FAILED. The IP might still be mismatched or session is stale.")
            return
        print("✅ Broker Authentication SUCCESSFUL! IP address is verified.")
        
        # 2. Check Live Quotes (Heartbeats / Data Guard foundation)
        print("\n--- 2. VERIFYING LIVE QUOTES (Rule 71 Data Guard Foundation) ---")
        test_symbols = [
            ("NSE", "26000", "NIFTY"), 
            ("NSE", "26009", "BANKNIFTY"), 
            ("BSE", "1", "SENSEX")
        ]
        
        # get_quotes_parallel expects [(token, exch), ...] for mStock
        query_list = [(token, exch) for exch, token, name in test_symbols]
        qs = api.get_quotes_parallel(query_list)
        
        for exch, token, name in test_symbols:
            # The key returned by get_quotes_parallel is the token
            spot = qs.get(token, {}).get('last_price', 0)
            if spot > 0:
                print(f"✅ {name}: LIVE SPOT PRICE = {spot}")
            else:
                print(f"⚠️ {name}: Spot price is {spot}. Market might be closed or quote fetch failed.")
                
        # 3. Check Indicator Data Fetch & Fallback Chain (Rules 51, 72, 12)
        print("\n--- 3. VERIFYING DATA FETCH & INDICATORS (Rules 51, 72 & 12) ---")
        symbols_to_test = [
            ('NIFTY', 'NSE', '26000', 'NIFTY'),
            ('BANKNIFTY', 'NSE', '26009', 'BANKNIFTY'),
            ('SENSEX', 'BSE', '1', 'SENSEX')
        ]
        
        for sym, exch, token, name in symbols_to_test:
            print(f"\nTesting Full Data Pipeline for {name}...")
            try:
                d_df, i_df, spot, adx, stable, fresh = get_market_data_with_indicators(api, sym, exch, token, name)
                
                if d_df is None or i_df is None:
                    print(f"❌ {name}: get_market_data_with_indicators returned None! Check logs for Data Fetch Error.")
                else:
                    vwap = i_df.iloc[-1].get('VWAP', 0) if 'VWAP' in i_df.columns else 'MISSING'
                    volume = i_df.iloc[-1].get('volume', 0) if 'volume' in i_df.columns else 'MISSING'
                    rsi = i_df.iloc[-1].get('RSI', 0)
                    macd = i_df.iloc[-1].get('MACD', 0)
                    
                    print(f"✅ {name}: Pipeline SUCCESS! (Stable: {stable}, Fresh: {fresh})")
                    print(f"   Spot: {spot}, VWAP: {vwap}, Volume: {volume}")
                    print(f"   RSI: {rsi:.2f}, Daily ADX: {adx:.2f}, MACD: {macd:.2f}")
                    
                    if volume == 0:
                        print(f"   ⚠️ Volume is 0. (Expected if Future Proxy or Market is pre-open)")
                    if 'volume' not in i_df.columns:
                        print(f"   ❌ FATAL: 'volume' column is entirely missing from i_df!")
            except Exception as e:
                print(f"❌ FATAL CRASH during {name} fetch!")
                traceback.print_exc()

        print("\n--- AUDIT COMPLETE ---")
        
    except Exception as e:
        print("❌ CRITICAL SCRIPT ERROR:")
        traceback.print_exc()

if __name__ == '__main__':
    run_audit()
