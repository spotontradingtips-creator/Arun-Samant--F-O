import json
import os
import sys
import pandas as pd
from datetime import datetime

# Add src to path
sys.path.append(os.getcwd())

from src.market_data import MStockAPI

def broker_api_historical_audit():
    print("AUDITING DIRECTLY VIA BROKER API (APRIL 1 - APRIL 10)...")
    try:
        api = MStockAPI()
        if not api.ensure_session_is_valid():
            print("API SESSION INVALID.")
            return

        # 1. Attempt to fetch historical trade list (API Source)
        # We'll try common endpoints if tradelist is restricted
        from_date = "2026-04-01"
        to_date = "2026-04-10"
        
        print(f"Requesting Trade List from {from_date} to {to_date}...")
        trades = api.get_historical_trades(from_date, to_date)
        
        if trades is None or not isinstance(trades, list):
            print("Broker API 'Tradelist' endpoint restricted or empty.")
            # Fallback: Pull from net positions if available (often only shows today)
            print("Checking currently reporting Ledger/P&L status...")
            # Note: For multi-day audit, if the API doesn't provide a tradelist, 
            # we rely on the consolidated ledger if available.
            return

        print(f"SUCCESS: Fetched {len(trades)} trades from Broker API.")
        
        # Process trades
        processed_trades = []
        for t in trades:
            # Normalize fields based on mStock response
            pnl = float(t.get('pnl', t.get('realized_pnl', 0.0)))
            processed_trades.append({
                'symbol': t.get('symbol', t.get('tradingsymbol')),
                'pnl': pnl,
                'date': t.get('date', t.get('trade_date'))
            })

        # Summary
        total_pnl = sum(t['pnl'] for t in processed_trades)
        wins = [t for t in processed_trades if t['pnl'] > 0]
        winrate = (len(wins) / len(processed_trades) * 100) if processed_trades else 0
        
        print("\n--- BROKER API AUDIT RESULTS ---")
        print(f"Total Trades: {len(processed_trades)}")
        print(f"Win Rate:     {winrate:.2f}%")
        print(f"Total P&L:    Rs {total_pnl:+,.2f}")
        print(f"ROI (Base 1L): {(total_pnl / 100000 * 100):.2f}%")

    except Exception as e:
        print(f"API AUDIT ERROR: {str(e)}")

if __name__ == '__main__':
    broker_api_historical_audit()
