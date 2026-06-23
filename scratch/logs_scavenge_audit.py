import os
import re
import pandas as pd
import glob
from datetime import datetime

def scavenge_logs():
    print("--- LOG-BASED HISTORICAL AUDIT ---")
    log_files = glob.glob("logs/trading_bot_*.log")
    
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
    master_trades['Entry_Time'] = pd.to_datetime(master_trades['Entry_Time'])
    print(f"Loaded {len(master_trades)} confirmed trades from CSVs.")
    
    audit_data = []
    
    # Improved patterns
    # SENSEX [CE]: MACD Histogram Momentum OK (Value: 90.44 >= 10.0 | Slope: 90.44 > 90.17)
    momentum_pattern = re.compile(r'(\w+) \[(CE|PE)\]: MACD Histogram Momentum OK \(Value: ([\-\d\.]+) [><]=? [ \-\d\.]+ \| Slope: [ \-\d\.]+ [><] ([\-\d\.]+)\)')
    # OK BANKNIFTY: All CE entry conditions met | RSI=49.06 | Daily ADX=47.43 | VIX=15.00
    ra_pattern = re.compile(r'OK (\w+): All (CE|PE) entry conditions met \| RSI=([\d\.]+) \| Daily ADX=([\d\.]+)')
    # PLACING ORDER: BUY 20 x SENSEX2641677300CE
    order_pattern = re.compile(r'PLACING ORDER: (BUY|SELL) \d+ x (\w+)')
    
    last_seen_mom = {} # key -> {hist, prev}
    last_seen_ra = {} # key -> {rsi, adx}
    
    for log_file in sorted(log_files):
        if "2026" not in log_file: continue
        print(f"  Parsing {os.path.basename(log_file)}...")
        with open(log_file, 'r', errors='ignore') as f:
            for line in f:
                ts_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
                if not ts_match: continue
                ts_str = ts_match.group(1)
                
                m_match = momentum_pattern.search(line)
                if m_match:
                    ticker, side, val, prev = m_match.groups()
                    key = f"{ticker}_{side}"
                    last_seen_mom[key] = {"val": float(val), "prev": float(prev)}
                
                ra_match = ra_pattern.search(line)
                if ra_match:
                    ticker, side, rsi, adx = ra_match.groups()
                    key = f"{ticker}_{side}"
                    last_seen_ra[key] = {"rsi": float(rsi), "adx": float(adx)}
                
                o_match = order_pattern.search(line)
                if o_match:
                    side_str, symbol = o_match.groups()
                    if side_str == "SELL": continue
                    
                    underlying = "NIFTY" if "NIFTY" in symbol else ("BANKNIFTY" if "BANK" in symbol else "SENSEX")
                    side = "PE" if "PE" in symbol else "CE"
                    key = f"{underlying}_{side}"
                    
                    if key in last_seen_mom:
                        entry = {
                            "ts": ts_str,
                            "symbol": symbol,
                            "underlying": underlying,
                            "hist": last_seen_mom[key]['val'],
                            "prev_hist": last_seen_mom[key]['prev'],
                            "rsi": last_seen_ra.get(key, {}).get('rsi', 50),
                            "adx": last_seen_ra.get(key, {}).get('adx', 0)
                        }
                        audit_data.append(entry)

    if not audit_data:
        print("Scavenge failed to find data.")
        return
        
    audit_df = pd.DataFrame(audit_data)
    print(f"Scavenged indicators for {len(audit_df)} entries.")
    
    final_results = []
    for _, scav in audit_df.iterrows():
        s_ts = pd.to_datetime(scav['ts'])
        # Try to find trade in CSV within 5 mins
        matches = master_trades[
            (master_trades['Entry_Time'] >= s_ts - pd.Timedelta(minutes=5)) & 
            (master_trades['Entry_Time'] <= s_ts + pd.Timedelta(minutes=5))
        ]
        
        if not matches.empty:
            trade = matches.iloc[0]
            jump = abs(scav['hist'] - scav['prev_hist'])
            hunter_took = (jump >= 2.0) and (scav['adx'] >= 30)
            
            final_results.append({
                "Date": scav['ts'],
                "P&L": trade['P&L'],
                "Winner": trade['P&L'] > 0,
                "Jump": jump,
                "ADX": scav['adx'],
                "Hunter_Decision": "TAKE" if hunter_took else "SKIP"
            })
            
    if not final_results:
        print("Could not match logs to P&L outcomes.")
        return
        
    df = pd.DataFrame(final_results)
    winners = df[df['Winner'] == True]
    losers = df[df['Winner'] == False]
    
    w_kept = len(winners[winners['Hunter_Decision'] == 'TAKE'])
    l_avoided = len(losers[losers['Hunter_Decision'] == 'SKIP'])
    
    print("\n" + "="*60)
    print("FINAL HUNTER AUDIT REPORT (JAN - APR 2026)")
    print("="*60)
    print(f"Total Bot Trades Analyzed: {len(df)}")
    print(f"Original Win Rate: {(len(winners)/len(df)*100):.1f}% ({len(winners)}W / {len(losers)}L)")
    print("-" * 60)
    print(f"WINNERS KEPT: {w_kept} / {len(winners)} ({(w_kept/len(winners)*100 if len(winners)>0 else 0):.1f}%)")
    print(f"LOSERS AVOIDED: {l_avoided} / {len(losers)} ({(l_avoided/len(losers)*100 if len(losers)>0 else 0):.1f}%)")
    print("-" * 60)
    
    new_w = w_kept
    new_l = len(losers) - l_avoided
    print(f"PROJECTED HUNTER WIN RATE: {(new_w/(new_w+new_l)*100):.1f}%")
    print(f"Capital Saved: Hunter would have skipped {l_avoided} of your losing trades.")
    print("="*60)

if __name__ == "__main__":
    scavenge_logs()
