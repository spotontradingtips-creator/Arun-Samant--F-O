
import sys
import os
import json
import pandas as pd
from datetime import datetime, timedelta
from src.market_data import MStockAPI
from src.trading_models import Position, TradeType, ExitReason

def sync_all():
    api = MStockAPI()
    if not api.access_token:
        print("Error: No access token. Please run START_BOT.bat first.")
        return

    # 1. Fetch Today's Net Positions (Manual + Bot)
    print("Fetching today's net positions...")
    net_pos = api.get_net_positions() or []
    print(f"Found {len(net_pos)} positions for today.")
    
    # 2. Fetch Historical Trades (Last 15 days)
    to_date = datetime.now().strftime("%Y-%m-%d")
    from_date = (datetime.now() - timedelta(days=15)).strftime("%Y-%m-%d")
    
    print(f"Fetching historical tradelist from {from_date} to {to_date}...")
    hist_trades = api.get_historical_trades(from_date, to_date) or []
    print(f"Found {len(hist_trades)} historical trade entries.")

    # 3. Analyze Trades
    # Combine Day results with Historical results
    # For mStock, /portfolio/positions with quantity 0 represents closed trades for the day.
    
    closed_today = []
    for p in net_pos:
        if p.get('quantity') == 0:
            # Reconstruct as a result
            symbol = p.get('tradingsymbol')
            pnl = p.get('realised', 0)
            closed_today.append({
                'symbol': symbol,
                'pnl': pnl,
                'win': pnl > 0,
                'type': 'Manual/Bot'
            })
            
    print(f"\nAnalyzed {len(closed_today)} closed trades from today:")
    for t in closed_today:
        status = "WIN" if t['win'] else "LOSS"
        print(f" - {t['symbol']}: Rs {t['pnl']:+,.2f} ({status})")

    # 4. Load Bot's daily_history.json
    bot_history = []
    if os.path.exists("data/daily_history.json"):
        with open("data/daily_history.json", "r") as f:
            bot_history = json.load(f)
    print(f"\nLoaded {len(bot_history)} trades from Bot Memory.")

    # 5. Summarize
    # Note: Bot memory might overlap with broker's today results.
    # We will provide a composite view.
    
    # Total wins/losses from Bot history
    bot_wins = sum(1 for p in bot_history if p.get('pnl', 0) > 0)
    bot_total = len(bot_history)
    
    # Today's results from Broker (likely mostly manual if bot just started)
    broker_wins = sum(1 for t in closed_today if t['win'])
    broker_total = len(closed_today)
    
    print("\n" + "="*40)
    print("      OVERALL PERFORMANCE SUMMARY")
    print("="*40)
    print(f"Bot Memory Trades   : {bot_total} (Wins: {bot_wins})")
    print(f"Today's Broker Trades: {broker_total} (Wins: {broker_wins})")
    
    # Combine for estimate (avoiding double counting if possible)
    # This is a bit tricky without unique IDs, so we report them separately for clarity.
    
    total_est = bot_total + broker_total
    wins_est = bot_wins + broker_wins
    overall_wr = (wins_est / total_est * 100) if total_est > 0 else 0
    
    print(f"Estimated Combined  : {total_est} trades")
    print(f"Overall Win Rate    : {overall_wr:.2f}%")
    print("="*40)

if __name__ == "__main__":
    sync_all()
