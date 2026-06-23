import json
import os
from collections import defaultdict

history_file = "data/daily_history.json"
if not os.path.exists(history_file):
    print(f"Error: {history_file} not found")
    exit(1)

with open(history_file, 'r') as f:
    trades = json.load(f)

# Structure to hold stats per index
stats = defaultdict(lambda: {
    'total_trades': 0,
    'wins': 0,
    'losses': 0,
    'total_pnl': 0.0,
    'best_trade': 0.0,
    'worst_trade': 0.0
})

for trade in trades:
    underlying = trade.get('underlying', 'UNKNOWN').upper()
    pnl = trade.get('pnl', 0.0)
    if pnl is None:
        pnl = 0.0
        
    # Standardize names
    if "NIFTY" in underlying and "BANK" not in underlying and "FIN" not in underlying:
        underlying = "NIFTY50"
    elif "BANK" in underlying:
        underlying = "BANKNIFTY"
    elif "SENSEX" in underlying:
        underlying = "SENSEX"
    elif "FIN" in underlying:
        underlying = "FINNIFTY"
        
    stats[underlying]['total_trades'] += 1
    stats[underlying]['total_pnl'] += pnl
    
    if pnl > 0:
        stats[underlying]['wins'] += 1
    elif pnl < 0:
        stats[underlying]['losses'] += 1
        
    if pnl > stats[underlying]['best_trade']:
        stats[underlying]['best_trade'] = pnl
    if pnl < stats[underlying]['worst_trade']:
        stats[underlying]['worst_trade'] = pnl

# Print markdown table
print("| Index | Total Trades | Win Rate | Total P&L (Rs) | Best Trade | Worst Trade |")
print("|-------|--------------|----------|----------------|------------|-------------|")

for index, data in sorted(stats.items(), key=lambda x: x[1]['total_pnl'], reverse=True):
    total = data['total_trades']
    wins = data['wins']
    win_rate = (wins / total * 100) if total > 0 else 0
    pnl = data['total_pnl']
    best = data['best_trade']
    worst = data['worst_trade']
    
    print(f"| {index} | {total} | {win_rate:.1f}% | Rs {pnl:,.2f} | Rs {best:,.2f} | Rs {worst:,.2f} |")
