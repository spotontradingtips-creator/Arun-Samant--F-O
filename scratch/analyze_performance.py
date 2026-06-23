import json
import re
from datetime import datetime
import os

history_file = r'c:\Antigravity\Arun Samant - F&O\data\daily_history.json'
log_files = [
    r'c:\Antigravity\Arun Samant - F&O\logs\trading_bot_20260429.log',
    r'c:\Antigravity\Arun Samant - F&O\logs\trading_bot_20260430.log'
]

def analyze_trades():
    with open(history_file, 'r') as f:
        data = json.load(f)
        
    real_trades = []
    
    for t in data:
        entry_time = t.get('entry_time', '')
        if '2026-04-29' in entry_time or '2026-04-30' in entry_time:
            reason = t.get('exit_reason', '')
            pnl = t.get('pnl', 0)
            
            # Filter out ghost trades (Broker Sync Reconciliation)
            if reason != 'Broker Sync Reconciliation' and t.get('exit_price', 0) > 0:
                real_trades.append(t)
                
    wins = 0
    losses = 0
    total_pnl = 0
    
    print("\n=== TRADE LIST ===")
    for t in real_trades:
        pnl = t.get('pnl', 0)
        total_pnl += pnl
        if pnl > 0: wins += 1
        else: losses += 1
        
        print(f"Date: {t['entry_time'][:10]} | Symbol: {t['option_symbol']} | Type: {t['trade_type']} | PnL: Rs {pnl:.2f} | Reason: {t.get('exit_reason')}")
        
    total_trades = wins + losses
    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
    
    print("\n=== PERFORMANCE SUMMARY ===")
    print(f"Total Real Trades: {total_trades}")
    print(f"Wins: {wins} | Losses: {losses}")
    print(f"Win Rate: {win_rate:.2f}%")
    print(f"Total Net PnL: Rs {total_pnl:.2f}")

    print("\n=== ENTRY CONDITION AUDIT ===")
    # Grep logs around the entry times
    for t in real_trades:
        entry_time_str = t['entry_time']
        # e.g. 2026-04-29T10:00:46
        dt = datetime.fromisoformat(entry_time_str)
        time_prefix = dt.strftime('%H:%M')
        date_str = dt.strftime('%Y%m%d')
        
        log_file = None
        for lf in log_files:
            if date_str in lf:
                log_file = lf
                break
                
        if log_file and os.path.exists(log_file):
            print(f"\nAuditing Log around {entry_time_str} for {t['underlying']}...")
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            # Find the line containing the exact minute or minute-1
            found = False
            for i, line in enumerate(lines):
                if time_prefix in line and (t['underlying'] in line or 'ENTRY' in line or 'TRIGGER' in line):
                    # Print context
                    start_idx = max(0, i - 5)
                    end_idx = min(len(lines), i + 5)
                    for j in range(start_idx, end_idx):
                        if 'LOGIC_SNAPSHOT' in lines[j] or 'Momentum' in lines[j] or 'ENTRY' in lines[j] or 'TRIGGER' in lines[j] or 'ADX' in lines[j] or 'RSI' in lines[j]:
                            print("   " + lines[j].strip())
                    found = True
                    break
            if not found:
                print("   Could not find log entry for exact time.")

if __name__ == '__main__':
    analyze_trades()
