import json
from datetime import datetime
from collections import defaultdict

def analyze_losses():
    try:
        with open('data/daily_history.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("History file not found.")
        return

    # Group by date
    daily_trades = defaultdict(list)
    for t in data:
        try:
            entry_time = datetime.fromisoformat(t['entry_time'])
            if entry_time.year < 2026: continue
            date_str = entry_time.strftime('%Y-%m-%d')
            daily_trades[date_str].append((entry_time, t))
        except Exception:
            continue

    first_trade_losses = []
    for date in sorted(daily_trades.keys()):
        trades = sorted(daily_trades[date], key=lambda x: x[0])
        first_trade = trades[0][1]
        pnl = float(first_trade.get('pnl', 0))
        if pnl < 0:
            first_trade_losses.append(first_trade)

    print("| Date | Time | Index | Duration (Min) | P&L (Rs) | Exit Reason |")
    print("| :--- | :--- | :--- | :--- | :--- | :--- |")
    
    for l in first_trade_losses:
        entry = datetime.fromisoformat(l['entry_time'])
        exit = datetime.fromisoformat(l['exit_time'])
        duration = (exit - entry).seconds // 60
        entry_time_str = entry.strftime('%H:%M:%S')
        print(f"| {l['entry_time'][:10]} | {entry_time_str} | {l['underlying']} | {duration} | {l['pnl']:.2f} | {l['exit_reason']} |")

if __name__ == '__main__':
    analyze_losses()
