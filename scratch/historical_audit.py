import os
import pandas as pd
import numpy as np
import yfinance as yf
import glob
import sys
from datetime import datetime, timedelta
import pytz

# Add project root to path
sys.path.append(os.getcwd())

from src.indicators import TechnicalIndicators

def perform_deep_audit():
    print("--- DEEP TRADING AUDIT (JAN 2026 - APR 2026) ---")
    ist = pytz.timezone("Asia/Kolkata")
    
    # 1. Load All Bot Trades from CSV logs
    log_files = glob.glob("logs/live_trades_*.csv")
    if not log_files:
        print("No local trade logs found.")
        return
    
    all_trades = []
    for f in log_files:
        df = pd.read_csv(f)
        all_trades.append(df)
    
    master_df = pd.concat(all_trades).drop_duplicates(subset=['Position_ID'])
    master_df['Entry_Time'] = pd.to_datetime(master_df['Entry_Time'])
    
    # Sort by time
    master_df = master_df.sort_values('Entry_Time')
    print(f"Loaded {len(master_df)} unique bot trades.")
    
    # 2. Setup Historical Data Cache (YFinance used for broad audit)
    # Mapping log symbols to YF tickers
    ticker_map = {
        "NIFTY50": "^NSEI",
        "NIFTY": "^NSEI",
        "BANKNIFTY": "^NSEBANK",
        "NIFTYBANK": "^NSEBANK",
        "SENSEX": "^BSESN",
        "FINNIFTY": "NIFTY_FIN_SERVICE.NS"
    }
    
    audit_results = {
        "Taken_Positive": 0,
        "Taken_Negative": 0,
        "Avoided_Negative": 0,
        "Missed_Positive": 0
    }
    
    details = []
    
    # 3. Group trades by underlying to minimize YF calls
    for underlying in master_df['Underlying'].unique():
        if underlying not in ticker_map:
            continue
            
        ticker = ticker_map[underlying]
        print(f"Auditing {underlying} trades (Ticker: {ticker})...")
        
        # Fetch 2 months of 15m data for audit
        # We fetch extra days to ensure indicator warm-up
        try:
            yf_df = yf.download(ticker, start="2026-01-01", end="2026-04-14", interval="15m", progress=False)
            if yf_df.empty:
                continue
            yf_df.columns = [col[0] if isinstance(col, tuple) else col for col in yf_df.columns]
            
            # Calculate Indicators for the WHOLE period
            close = yf_df['Close']
            high = yf_df['High']
            low = yf_df['Low']
            
            # Use bot's own calculation module
            rsi = TechnicalIndicators.calculate_rsi(close)
            macd, macd_signal, macd_hist = TechnicalIndicators.calculate_macd(close)
            adx, _, _ = TechnicalIndicators.calculate_adx(high, low, close)
            
            # Filter trades for this underlying
            underlying_trades = master_df[master_df['Underlying'] == underlying]
            
            for _, trade in underlying_trades.iterrows():
                entry_time = trade['Entry_Time']
                if entry_time.tzinfo is None:
                    entry_time = ist.localize(entry_time)
                else:
                    entry_time = entry_time.tz_convert(ist)
                
                # Align to 15m bar end (indicators are calculated on closed bars)
                bar_time = entry_time.replace(second=0, microsecond=0)
                
                # Find the indicator value at or just before this entry
                try:
                    # Get indices available till this bar
                    available_indices = yf_df.index[yf_df.index <= bar_time]
                    if len(available_indices) < 2:
                        continue
                        
                    idx = available_indices[-1]
                    prev_idx = available_indices[-2]
                    
                    curr_hist = macd_hist.loc[idx]
                    prev_hist = macd_hist.loc[prev_idx]
                    curr_rsi = rsi.loc[idx]
                    prev_rsi = rsi.loc[prev_idx]
                    curr_adx = adx.loc[idx]
                    
                    # Hunter Logic Check
                    jump = curr_hist - prev_hist
                    is_ce = trade['Type'] == 'CALL'
                    
                    # 1. MACD Jump
                    macd_pass = False
                    if is_ce:
                        if curr_hist > 8 and jump >= 2.0: macd_pass = True
                    else:
                        if curr_hist < -8 and jump <= -2.0: macd_pass = True
                        
                    # 2. RSI Flow
                    rsi_pass = (curr_rsi > prev_rsi) if is_ce else (curr_rsi < prev_rsi)
                    
                    # 3. ADX Power
                    adx_pass = curr_adx >= 30
                    
                    # HUNTER DECISION
                    hunter_would_take = macd_pass and rsi_pass and adx_pass
                    is_winner = trade['P&L'] > 0
                    
                    if hunter_would_take:
                        if is_winner: audit_results["Taken_Positive"] += 1
                        else: audit_results["Taken_Negative"] += 1
                    else:
                        if is_winner: audit_results["Missed_Positive"] += 1
                        else: audit_results["Avoided_Negative"] += 1
                        
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"Error auditing {underlying}: {e}")

    # 4. Final Formatting
    print("\n" + "="*50)
    print("FINAL HUNTER AUDIT REPORT")
    print("="*50)
    total = sum(audit_results.values())
    print(f"Total Bot Trades Analyzed: {total}")
    print("-" * 50)
    print(f"WINNERS CAUGHT: {audit_results['Taken_Positive']} (Great!)")
    print(f"LOSERS AVOIDED: {audit_results['Avoided_Negative']} (Saved Money!)")
    print(f"LOSERS STILL TAKEN: {audit_results['Taken_Negative']} (Remaining Risk)")
    print(f"WINNERS MISSED: {audit_results['Missed_Positive']} (Cost of being picky)")
    
    avoidance_rate = (audit_results['Avoided_Negative'] / (audit_results['Avoided_Negative'] + audit_results['Taken_Negative'])) * 100 if (audit_results['Avoided_Negative'] + audit_results['Taken_Negative']) > 0 else 0
    print("-" * 50)
    print(f"The 'Hunter' Mode would have avoided {avoidance_rate:.1f}% of your losses.")
    print("="*50)

if __name__ == "__main__":
    perform_deep_audit()
