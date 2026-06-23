import json
import os
import sys

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.market_data import MStockAPI
from src.utils import console

def fetch_real_pnl():
    print("Fetching Direct P&L from Broker API...")
    api = MStockAPI()
    if not api.ensure_session_is_valid():
        print("Error: API Session invalid.")
        return
        
    positions = api.get_net_positions()
    if positions is None:
        print("Error: Could not fetch positions.")
        return
        
    total_realized_pnl = 0.0
    print("\n--- Current Broker Positions ---")
    for pos in positions:
        tsym = pos.get('tradingsymbol')
        # mStock provides 'pnl' for realized/unrealized? 
        # Usually 'pnl' in positions is the current P&L of the position.
        # If quantity is 0, it's realized P&L.
        pnl = float(pos.get('pnl', 0.0))
        qty = int(pos.get('netqty', 0))
        
        status = "CLOSED" if qty == 0 else "OPEN"
        print(f"Symbol: {tsym} | Qty: {qty} | P&L: Rs {pnl:.2f} | [{status}]")
        
        total_realized_pnl += pnl
        
    print(f"\nTOTAL CALCULATED P&L: Rs {total_realized_pnl:.2f}")
    
    # Save to a temporary file for the agent to read
    with open('artifacts/direct_pnl_report.json', 'w') as f:
        json.dump({
            'total_pnl': total_realized_pnl,
            'positions': positions
        }, f, indent=4)

if __name__ == "__main__":
    fetch_real_pnl()
