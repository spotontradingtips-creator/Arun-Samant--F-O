
import json
from datetime import datetime
from collections import defaultdict

def analyze_week():
    try:
        with open('data/daily_history.json', 'r') as f:
            trades = json.load(f)
    except Exception as e:
        print(f"Error loading history: {e}")
        return

    # Filter for this week (Apr 13 - Apr 17)
    week_start = datetime(2026, 4, 13).date()
    week_end = datetime(2026, 4, 17).date()
    
    weekly_trades = []
    for t in trades:
        entry_time = datetime.fromisoformat(t['entry_time'].replace('+05:30', '')).date()
        if week_start <= entry_time <= week_end:
            weekly_trades.append(t)
            
    if not weekly_trades:
        print("No trades found for this week.")
        return

    # Metrics
    total_trades = len(weekly_trades)
    winning_trades = [t for t in weekly_trades if t['pnl'] > 0]
    losing_trades = [t for t in weekly_trades if t['pnl'] <= 0]
    
    win_rate = (len(winning_trades) / total_trades) * 100
    total_pnl = sum(t['pnl'] for t in weekly_trades)
    
    avg_win = sum(t['pnl'] for t in winning_trades) / len(winning_trades) if winning_trades else 0
    avg_loss = sum(t['pnl'] for t in losing_trades) / len(losing_trades) if losing_trades else 0
    
    # Per Index
    index_stats = defaultdict(lambda: {'pnl': 0, 'wins': 0, 'total': 0})
    for t in weekly_trades:
        idx = t['underlying']
        index_stats[idx]['pnl'] += t['pnl']
        index_stats[idx]['total'] += 1
        if t['pnl'] > 0:
            index_stats[idx]['wins'] += 1
            
    # Exit Reason Analysis
    exit_reasons = defaultdict(int)
    for t in weekly_trades:
        exit_reasons[t['exit_reason']] += 1

    # Daily P&L for Drawdown
    daily_pnl = defaultdict(float)
    for t in weekly_trades:
        day = datetime.fromisoformat(t['entry_time'].replace('+05:30', '')).date()
        daily_pnl[day] += t['pnl']
        
    print(f"--- WEEKLY PERFORMANCE AUDIT (Apr 13 - Apr 17) ---")
    print(f"Total Trades: {total_trades}")
    print(f"Win Rate: {win_rate:.2f}%")
    print(f"Total Net P&L: Rs {total_pnl:.2f}")
    print(f"Avg Win: Rs {avg_win:.2f} | Avg Loss: Rs {avg_loss:.2f}")
    print(f"Risk/Reward: 1 : {abs(avg_win/avg_loss):.2f}" if avg_loss != 0 else "N/A")
    
    print(f"\n--- PERFORMANCE BY INDEX ---")
    for idx, stats in index_stats.items():
        wr = (stats['wins'] / stats['total']) * 100
        print(f"{idx:10}: P&L: Rs {stats['pnl']:8.2f} | Trades: {stats['total']:2} | WR: {wr:5.2f}%")
        
    print(f"\n--- EXIT REASON INSIGHTS ---")
    for reason, count in exit_reasons.items():
        print(f"{reason:20}: {count} trades")

    print(f"\n--- DAILY BREAKDOWN ---")
    for day in sorted(daily_pnl.keys()):
        print(f"{day}: Rs {daily_pnl[day]:.2f}")

if __name__ == "__main__":
    analyze_week()
