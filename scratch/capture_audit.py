import json
from datetime import datetime

def analyze_capture_efficiency():
    with open('data/daily_history.json', 'r') as f:
        history = json.load(f)
    
    # Filter for last 2 weeks (approx)
    recent_trades = [t for t in history if "2026-04" in t['entry_time']]
    
    print(f"--- CAPTURE EFFICIENCY AUDIT (Last {len(recent_trades)} Trades) ---")
    
    small_profits = 0
    big_runners = 0
    stopped_out = 0
    
    for t in recent_trades:
        pnl = t.get('pnl', 0)
        max_seen = t.get('max_pnl_reached', 0)
        reason = t.get('exit_reason', 'Unknown')
        
        # Capture Efficiency = Actual P&L / Max P&L Reached
        efficiency = (pnl / max_seen * 100) if max_seen > 500 else 0
        
        if pnl > 0 and pnl < 300:
            small_profits += 1
            if max_seen > 800:
                print(f"MISS: {t['underlying']} {t['trade_type']} | P&L: {pnl:.2f} | Max Was: {max_seen:.2f} | Reason: {reason}")
        
        if pnl > 1000:
            big_runners += 1
            
        if "Stop Loss" in reason:
            stopped_out += 1
            
    print(f"\nSummary:")
    print(f"  Small Profits (< Rs 300): {small_profits}")
    print(f"  Big Runners (> Rs 1000): {big_runners}")
    print(f"  Hard Stop Losses: {stopped_out}")
    print(f"  Total Recent Trades: {len(recent_trades)}")

if __name__ == "__main__":
    analyze_capture_efficiency()
