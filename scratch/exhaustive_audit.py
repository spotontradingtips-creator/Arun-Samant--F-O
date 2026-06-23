import re
import os
from datetime import datetime

def exhaustive_audit():
    print("STARTING EXHAUSTIVE LOG-SCAN AUDIT (APRIL 1 - APRIL 10)...")
    log_dir = 'logs'
    trades = []
    
    # Regex to catch different log styles
    # Style 1: EXIT SUCCESSFUL: SYMBOL | Reason: ... | P&L: Rs XXX.XX
    exit_regex = re.compile(r"EXIT SUCCESSFUL: (.*?) \| Reason: (.*?) \| P&L: Rs ([\d\-\.,]+)")
    # Style 2: TRADE CLOSED: SYMBOL ... P&L: XXX
    closed_regex = re.compile(r"TRADE CLOSED: (.*?) .*? P&L: ([\d\-\.,]+)")

    log_files = sorted([f for f in os.listdir(log_dir) if f.startswith('trading_bot_202604')])
    
    for log_file in log_files:
        date_str = log_file.split('_')[2].replace('.log', '')
        # Only April 2026
        if not date_str.startswith('202604'): continue
        
        path = os.path.join(log_dir, log_file)
        print(f"Scanning {log_file}...")
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    match1 = exit_regex.search(line)
                    if match1:
                        symbol = match1.group(1).strip()
                        reason = match1.group(2).strip()
                        pnl_str = match1.group(3).replace(',', '')
                        trades.append({
                            'date': date_str,
                            'symbol': symbol,
                            'pnl': float(pnl_str),
                            'reason': reason
                        })
                        continue
                    
                    match2 = closed_regex.search(line)
                    if match2:
                        symbol = match2.group(1).strip()
                        pnl_str = match2.group(2).replace(',', '')
                        trades.append({
                            'date': date_str,
                            'symbol': symbol,
                            'pnl': float(pnl_str),
                            'reason': 'Closed'
                        })
        except Exception as e:
            print(f"Error reading {log_file}: {e}")

    # Deduplicate by Symbol + Date + P&L approx (to avoid counting same log entry twice)
    unique_trades = []
    seen = set()
    for t in trades:
        # Create a unique key
        key = f"{t['date']}_{t['symbol']}_{round(t['pnl'], 2)}"
        if key not in seen:
            unique_trades.append(t)
            seen.add(key)

    # Sort by date
    unique_trades.sort(key=lambda x: x['date'])

    print("\n--- AUDIT RESULTS (FOUND VIA LOG SCRAPING) ---")
    total_pnl = 0.0
    wins = 0
    losses = 0
    daily_stats = {}
    
    for t in unique_trades:
        total_pnl += t['pnl']
        if t['pnl'] > 0: wins += 1
        else: losses += 1
        
        d = t['date']
        if d not in daily_stats: daily_stats[d] = 0.0
        daily_stats[d] += t['pnl']

    for d, p in sorted(daily_stats.items()):
        print(f"Date: {d} | Daily P&L: Rs {p:+,.2f}")

    total_trades = wins + losses
    winrate = (wins / total_trades * 100) if total_trades > 0 else 0
    
    print("\n--- FINAL SUMMARY ---")
    print(f"Total Unique Trades: {total_trades}")
    print(f"Win Rate:           {winrate:.2f}%")
    print(f"Total Realized P&L: Rs {total_pnl:+,.2f}")
    
    # Check if there's any trade on April 1st
    apr1 = [t for t in unique_trades if t['date'] == '20260401']
    print(f"April 1st Trades:    {len(apr1)}")

if __name__ == '__main__':
    exhaustive_audit()
