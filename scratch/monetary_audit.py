import os
import re
import pandas as pd
import glob
import yfinance as yf
from datetime import datetime
import pytz

def calculate_detailed_pnl_audit():
    print("--- DETAILED MONETARY HUNTER AUDIT (MARCH-APRIL) ---")
    ist = pytz.timezone("Asia/Kolkata")
    
    # 1. Load Bot Trades
    trade_csvs = glob.glob("logs/live_trades_*.csv")
    all_trades = []
    for f in trade_csvs:
        df = pd.read_csv(f)
        all_trades.append(df)
    
    if not all_trades:
        print("No trade CSVs found.")
        return
        
    master_trades = pd.concat(all_trades).drop_duplicates(subset=['Position_ID'])
    master_trades['Entry_Time'] = pd.to_datetime(master_trades['Entry_Time']).dt.tz_convert(ist)
    
    # Focus on March/April (Last 60 days for 15m YF data)
    start_date = ist.localize(datetime(2026, 3, 1))
    master_trades = master_trades[master_trades['Entry_Time'] >= start_date].sort_values('Entry_Time')
    print(f"Auditing {len(master_trades)} trades from March 1st onwards.")
    
    # 2. Fetch Historical Indicators (Broad cache)
    tickers = {"NIFTY50": "^NSEI", "BANKNIFTY": "^NSEBANK", "SENSEX": "^BSESN", "FINNIFTY": "NIFTY_FIN_SERVICE.NS"}
    history_cache = {}
    
    # Simple Technical Analysis Mock (Matches bot modules)
    def get_indicators(df):
        # 1. RSI
        delta = df['Close'].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.ewm(alpha=1/14, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1/14, adjust=False).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        # 2. MACD
        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        hist = macd - signal
        
        # 3. ADX
        # Simplified ADX logic for audit
        plus_dm = df['High'].diff().clip(lower=0)
        minus_dm = -df['Low'].diff().clip(upper=0)
        tr = pd.concat([df['High'] - df['Low'], (df['High'] - df['Close'].shift()).abs(), (df['Low'] - df['Close'].shift()).abs()], axis=1).max(axis=1)
        atr = tr.rolling(14).mean()
        high_mask = plus_dm > minus_dm
        low_mask = minus_dm > plus_dm
        plus_dm[~high_mask] = 0
        minus_dm[~low_mask] = 0
        plus_di = 100 * (plus_dm.rolling(14).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(14).mean() / atr)
        dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di)
        adx = dx.rolling(14).mean()
        
        return rsi, hist, adx

    # 3. RUN AUDIT
    taken_winners_pnl = 0
    taken_losers_pnl = 0
    skipped_winners_pnl = 0
    skipped_losers_pnl = 0
    
    taken_count = 0
    skipped_count = 0
    
    for underlying in master_trades['Underlying'].unique():
        if underlying not in tickers: continue
        sym = tickers[underlying]
        print(f"  Fetching history for {underlying}...")
        df = yf.download(sym, start="2026-02-15", end="2026-04-14", interval="15m", progress=False)
        if df.empty: continue
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
        df.index = df.index.tz_convert(ist)
        
        rsi, hist, adx = get_indicators(df)
        
        subset = master_trades[master_trades['Underlying'] == underlying]
        for _, trade in subset.iterrows():
            entry_time = trade['Entry_Time']
            # Find the candle ending at or just before entry
            available = rsi.index[rsi.index <= entry_time]
            if len(available) < 2: continue
            
            idx = available[-1]
            prev_idx = available[-2]
            
            # Hunter Logic
            curr_hist = hist.loc[idx]
            prev_hist = hist.loc[prev_idx]
            curr_rsi = rsi.loc[idx]
            prev_rsi = rsi.loc[prev_idx]
            curr_adx = adx.loc[idx]
            
            jump = abs(curr_hist - prev_hist)
            # Hunter take condition: Jump >= 2.0 AND ADX >= 30 AND RSI Flow
            # Note: We added RSI Flow to the proposal
            is_ce = trade['Type'] == 'CALL'
            rsi_flow = (curr_rsi > prev_rsi) if is_ce else (curr_rsi < prev_rsi)
            
            hunter_take = (jump >= 2.0) and (curr_adx >= 30) and rsi_flow
            
            pnl = trade['P&L']
            if hunter_take:
                taken_count += 1
                if pnl > 0: taken_winners_pnl += pnl
                else: taken_losers_pnl += pnl
            else:
                skipped_count += 1
                if pnl > 0: skipped_winners_pnl += pnl
                else: skipped_losers_pnl += pnl

    # 4. REPORT
    print("\n" + "="*60)
    print("FINAL MONETARY AUDIT RESULTS")
    print("="*60)
    print(f"TRADES ANALYSIS (Hunter Mode vs Original)")
    print("-" * 60)
    print(f"Hunter would have TAKEN {taken_count} trades.")
    print(f"  -> Profit from Winners:  Rs {taken_winners_pnl:,.2f}")
    print(f"  -> Loss from Mistakes:  Rs {taken_losers_pnl:,.2f}")
    print(f"  NET EXPECTANCY:          Rs {(taken_winners_pnl + taken_losers_pnl):,.2f}")
    print("-" * 60)
    print(f"Hunter would have SKIPPED {skipped_count} trades.")
    print(f"  -> Winners Missed:       Rs {skipped_winners_pnl:,.2f}")
    print(f"  -> CAPITAL RESCUED:     Rs {abs(skipped_losers_pnl):,.2f}  ( !!! )")
    print("-" * 60)
    
    original_net = (taken_winners_pnl + taken_losers_pnl + skipped_winners_pnl + skipped_losers_pnl)
    hunter_net = (taken_winners_pnl + taken_losers_pnl)
    improvement = hunter_net - original_net
    
    print(f"ORIGINAL NET P&L:        Rs {original_net:,.2f}")
    print(f"PROPOSED NET P&L:        Rs {hunter_net:,.2f}")
    print(f"TOTAL SYSTEM GAIN:       Rs {improvement:,.2f}")
    print("="*60)

if __name__ == "__main__":
    calculate_detailed_pnl_audit()
