import re
import os
from collections import defaultdict

def precision_audit():
    print("--- PRECISION LOG RECONSTRUCTION (APRIL 1 - APRIL 10) ---")
    log_dir = 'logs'
    
    # Regex Patterns
    # 1. Buy Stage: ORDER PLACED: NIFTY26APR22850CE | Qty: 65 | Price: 120.00
    buy_re = re.compile(r"ORDER (?:PLACED|SUCCESSFUL).*?([A-Z0-9\-\_]+) \| Qty: (\d+) \| (?:Price|Avg): ([\d\-\.]+)")
    # 2. Sell Stage: EXIT SUCCESSFUL: NIFTY... | Reason: ... | P&L: Rs XXX
    # (Matches what actually completed)
    exit_re = re.compile(r"EXIT SUCCESSFUL: ([A-Z0-9\-\_]+) .*? P&L: Rs ([\d\-\.,]+)")
    
    log_files = sorted([f for f in os.listdir(log_dir) if f.startswith('trading_bot_202604')])
    
    daily_closed_pnl = defaultdict(float)
    daily_trades_count = defaultdict(int)
    all_trade_details = []

    for log_file in log_files:
        date_str = log_file.split('_')[2].replace('.log', '')
        path = os.path.join(log_dir, log_file)
        
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                # Catch Exits (Actual realization)
                exit_match = exit_re.search(line)
                if exit_match:
                    symbol = exit_match.group(1).split('_')[0] # Get root symbol
                    pnl_raw = exit_match.group(2).replace(',', '')
                    try:
                        pnl = float(pnl_raw)
                        daily_closed_pnl[date_str] += pnl
                        daily_trades_count[date_str] += 1
                        all_trade_details.append({'date': date_str, 'symbol': symbol, 'pnl': pnl})
                    except: pass
                    continue
                
                # Catch 'Broker Sync Reconciliation' / 'Zombie' removals (Hidden P&L)
                if "Broker Sync Reconciliation" in line and "P&L: Rs" in line:
                    # Line: 2026-04-06 ... EXIT SUCCESSFUL: ... Reason: Broker Sync Reconciliation | P&L: Rs -13731.25
                    pass # Handled by exit_re above if format matches

    # Print Report
    print(f"{'Date':<12} | {'Trades':<8} | {'P&L Result':<15}")
    print("-" * 40)
    total_wins = 0
    total_count = 0
    grand_total_pnl = 0

    for d in sorted(daily_closed_pnl.keys()):
        p = daily_closed_pnl[d]
        c = daily_trades_count[d]
        print(f"{d:<12} | {c:<8} | Rs {p:+,.2f}")
        grand_total_pnl += p
        total_count += c

    wins_list = [t for t in all_trade_details if t['pnl'] > 0]
    win_rate = (len(wins_list) / total_count * 100) if total_count > 0 else 0

    print("-" * 40)
    print(f"GRAND TOTAL P&L: Rs {grand_total_pnl:+,.2f}")
    print(f"WIN RATE:        {win_rate:.2f}% ({len(wins_list)} wins / {total_count} trades)")
    print(f"ROI (1L Base):   {(grand_total_pnl / 100000 * 100):.2f}%")

if __name__ == '__main__':
    precision_audit()
