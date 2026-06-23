import json
from datetime import datetime
from collections import defaultdict

def analyze():
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
            entry_time_str = t['entry_time']
            # ISO format: 2026-02-09T11:08:42.839610+05:30
            # fromisoformat handles this correctly
            entry_time = datetime.fromisoformat(entry_time_str)
            
            # Since Jan 2026 (User said 'since Jan')
            if entry_time.year < 2026: continue
            
            date_str = entry_time.strftime('%Y-%m-%d')
            daily_trades[date_str].append((entry_time, t))
        except Exception as e:
            continue

    first_trades = []
    # Dates are sorted naturally
    for date in sorted(daily_trades.keys()):
        # Sort trades of the day by entry time
        trades_of_day = sorted(daily_trades[date], key=lambda x: x[0])
        # The 1st trade of the day based on entry time
        first_trades.append(trades_of_day[0][1])

    wins = 0
    losses = 0
    total_earned = 0.0
    total_lost = 0.0
    
    print("| Date | Index | Type | P&L (Rs) | Status | Exit Reason |")
    print("| :--- | :--- | :--- | :--- | :--- | :--- |")
    
    for t in first_trades:
        pnl = float(t.get('pnl', 0.0))
        status = "WIN" if pnl > 0 else "LOSS"
        if pnl > 0:
            wins += 1
            total_earned += pnl
        else:
            losses += 1
            total_lost += abs(pnl)
            
        date = t['entry_time'][:10]
        underlying = t['underlying']
        trade_type = t['trade_type']
        reason = t.get('exit_reason', 'N/A')
        
        print(f"| {date} | {underlying} | {trade_type} | {pnl:+.2f} | {status} | {reason} |")

    total_days = len(first_trades)
    winrate = (wins / total_days * 100) if total_days > 0 else 0
    net_pnl = total_earned - total_lost

    print("\n### Performance Summary: ONLY 1st Trades of the Day")
    print(f"- **Period Investigated**: Jan 2026 to Present")
    print(f"- **Total Trading Days**: {total_days}")
    print(f"- **Wins (1st Trade)**: {wins}")
    print(f"- **Losses (1st Trade)**: {losses}")
    print(f"- **Win Rate**: **{winrate:.2f}%**")
    print(f"- **Gross Profit**: Rs {total_earned:,.2f}")
    print(f"- **Gross Loss**: Rs {total_lost:,.2f}")
    print(f"- **Net P&L (1st Trade Only)**: **Rs {net_pnl:+,.2f}**")

if __name__ == '__main__':
    analyze()
