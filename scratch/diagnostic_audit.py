import sys
import os
import pandas as pd
import yfinance as yf
from datetime import datetime
import pytz

# Add project root to path
sys.path.append(os.getcwd())

from src.market_data import MStockAPI
from src.indicators import TechnicalIndicators
from src.live_indicators import LiveIndicators

def diagnostic_audit():
    print("--- SYSTEM RSI DIAGNOSTIC ---")
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)
    print(f"Time (IST): {now.strftime('%Y-%m-%d %H:%M:%S')}")
    
    api = MStockAPI()
    live_ind = LiveIndicators(api)
    
    # We will fetch indicators exactly as the dashboard/bot does
    summary = live_ind.get_all_indicators()
    
    indices = [
        ("NIFTY50", "^NSEI"),
        ("BANKNIFTY", "^NSEBANK"),
        ("SENSEX", "^BSESN")
    ]
    
    audit_data = []
    
    for key, yf_ticker in indices:
        bot_data = summary.get(key, {})
        bot_rsi = bot_data.get('intraday_15m', {}).get('rsi', 0)
        bot_price = bot_data.get('spot_price', 0)
        
        # Cross-check with YFinance
        try:
            yf_df = yf.download(yf_ticker, period="10d", interval="15m", progress=False)
            if not yf_df.empty:
                yf_df.columns = [col[0] if isinstance(col, tuple) else col for col in yf_df.columns]
                # Calculate RSI using bot's own logic on YFinance data
                yf_rsi = TechnicalIndicators.calculate_rsi(yf_df['Close']).iloc[-1]
                yf_price = yf_df['Close'].iloc[-1]
            else:
                yf_rsi = 0
                yf_price = 0
        except:
            yf_rsi = 0
            yf_price = 0
            
        audit_data.append({
             "Index": key,
             "Bot RSI": f"{bot_rsi:.2f}",
             "YF RSI": f"{yf_rsi:.2f}",
             "Diff": f"{abs(bot_rsi - yf_rsi):.2f}",
             "Bot Price": f"{bot_price:.2f}",
             "YF Price": f"{yf_price:.2f}"
        })

    # Print Report
    print("\n" + "="*80)
    print(f"{'Index':<12} | {'Bot RSI':<10} | {'YF RSI':<10} | {'Diff':<6} | {'Bot Price':<12} | {'YF Price'}")
    print("-" * 80)
    for row in audit_data:
        print(f"{row['Index']:<12} | {row['Bot RSI']:<10} | {row['YF RSI']:<10} | {row['Diff']:<6} | {row['Bot Price']:<12} | {row['YF Price']}")
    print("="*80)
    
    # VIX
    print(f"VIX: {summary.get('VIX', 'N/A')}")

if __name__ == "__main__":
    diagnostic_audit()
