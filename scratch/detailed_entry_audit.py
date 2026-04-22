
import sys
import os
import pandas as pd
import yfinance as yf
from datetime import datetime
import pytz

# Add src to path
sys.path.insert(0, os.getcwd())

from src.market_data import MStockAPI
from src.indicators import TechnicalIndicators

def detailed_audit():
    api = MStockAPI()
    
    indices = [
        {"name": "NIFTY", "exch": "NSE", "token": "26000", "ticker": "^NSEI"},
        {"name": "BANKNIFTY", "exch": "NSE", "token": "26009", "ticker": "^NSEBANK"},
        {"name": "SENSEX", "exch": "BSE", "token": "51", "ticker": "^BSESN"}
    ]
    
    print(f"\n{'='*100}")
    print(f"DETAILED ENTRY CONDITIONS AUDIT | Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*100}\n")
    
    for item in indices:
        name = item["name"]
        exch = item["exch"]
        token = item["token"]
        ticker = item["ticker"]
        
        # 1. DAILY ADX (YFinance + Broker Injection)
        daily_adx = 0
        try:
            df_yf = yf.download(ticker, period="2y", interval="1d", progress=False)
            if isinstance(df_yf.columns, pd.MultiIndex):
                df_yf.columns = [col[0] for col in df_yf.columns]
            df_yf = df_yf.rename(columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close'})
            
            quote = api.get_quote(name, exch)
            spot = quote.get('last_price', 0) if quote else 0
            if quote and 'ohlc' in quote:
                q_ohlc = quote['ohlc']
                ist = pytz.timezone("Asia/Kolkata")
                today_ts = pd.Timestamp(datetime.now(ist).date())
                today_bar = pd.DataFrame([{'open': q_ohlc['open'], 'high': q_ohlc['high'], 'low': q_ohlc['low'], 'close': spot}], index=[today_ts])
                if today_ts in df_yf.index: df_yf.update(today_bar)
                else: df_yf = pd.concat([df_yf, today_bar])

            adx, _, _ = TechnicalIndicators.calculate_adx(df_yf['high'], df_yf['low'], df_yf['close'])
            daily_adx = adx.iloc[-1]
        except: pass

        # 2. 15M INDICATORS (Hybrid)
        i_df, _ = api.get_hybrid_history(name, exch, token, "15minute", days=10)
        
        rsi_val = 0
        rsi_rising = False
        hist_jump = 0
        
        if i_df is not None and not i_df.empty:
            macd, signal, hist = TechnicalIndicators.calculate_macd(i_df['close'])
            rsi = TechnicalIndicators.calculate_rsi(i_df['close'])
            
            rsi_val = rsi.iloc[-1]
            rsi_rising = rsi.iloc[-1] > rsi.iloc[-2]
            rsi_falling = rsi.iloc[-1] < rsi.iloc[-2]
            hist_jump = hist.iloc[-1] - hist.iloc[-2]
        
        print(f"--- {name} (Spot: {spot:.2f}) ---")
        print(f"  [ADX GUARD] Daily ADX: {daily_adx:.2f} | Standard (>20): {'OK' if daily_adx > 20 else 'FAIL'} | Hunter (>30): {'OK' if daily_adx > 30 else 'FAIL'}")
        print(f"  [RSI AUDIT] 15m RSI: {rsi_val:.2f} | Range (30-70): {'OK' if 30 <= rsi_val <= 70 else 'FAIL'} | Flow: {'RISING' if rsi_rising else 'FALLING'}")
        print(f"  [MACD JUMP] 15m Hist Jump: {hist_jump:+.2f} | Threshold (>= +2.0 for CE, <= -2.0 for PE)")
        
        # CE Condition Check
        ce_met = daily_adx > 20 and 30 <= rsi_val <= 70 and rsi_rising and hist_jump >= 2.0
        pe_met = daily_adx > 20 and 30 <= rsi_val <= 70 and rsi_falling and hist_jump <= -2.0
        
        print(f"\n  >> CE ENTRY STATUS: {'READY' if ce_met else 'NOT MET'}")
        print(f"  >> PE ENTRY STATUS: {'READY' if pe_met else 'NOT MET'}")
        print("-" * 60)

if __name__ == "__main__":
    detailed_audit()
