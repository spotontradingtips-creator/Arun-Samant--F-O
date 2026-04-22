import json
import os
import sys
from datetime import datetime

# Add src to path
sys.path.append(os.getcwd())

from src.market_data import MStockAPI

def direct_broker_truth():
    print("RUNNING DIRECT API AUDIT...")
    try:
        api = MStockAPI()
        if not api.ensure_session_is_valid():
            print("API SESSION INVALID. Please run AUTHENTICATE.bat first.")
            return

        # 1. Fetch Net Positions (Today's Realized + MTM)
        positions = api.get_net_positions()
        
        if positions is None:
            print("COULD NOT FETCH POSITIONS FROM API.")
            return

        print("--- BROKER POSITIONS (DIRECT API) ---")
        total_realized_pnl = 0.0
        active_mtm = 0.0
        
        if not positions:
            print("No positions active today.")
        else:
            for p in positions:
                sym = str(p.get('tradingsymbol', 'UNKNOWN'))
                qty = int(p.get('netqty', 0))
                rpnl = float(p.get('realizedpnl', 0.0))
                upnl = float(p.get('unrealizedpnl', p.get('pnl', 0.0)))
                
                total_realized_pnl += rpnl
                active_mtm += upnl
                
                status = "OPEN" if qty != 0 else "CLOSED"
                print(f"- {sym: <25} | {status: <6} | Realized: {rpnl:+,.2f} | MTM: {upnl:+,.2f}")

        # 2. Update Local State to match API exactly
        print("--- STATE SYNC CHECK ---")
        print(f"Broker Realized: {total_realized_pnl:,.2f}")
        
        try:
            with open('data/daily_state.json', 'r') as f:
                state = json.load(f)
                local_pnl = state.get('daily_pnl', 0.0)
                print(f"Local Bot P&L:  {local_pnl:,.2f}")
                
                if abs(local_pnl - total_realized_pnl) > 0.01:
                    print("SYNC MISMATCH. Correcting local state...")
                    state['daily_pnl'] = total_realized_pnl
                    if total_realized_pnl > state.get('daily_max_pnl', 0.0):
                         state['daily_max_pnl'] = total_realized_pnl
                    
                    with open('data/daily_state.json', 'w') as fw:
                        json.dump(state, fw, indent=2)
                    print("DONE: Local state updated to match Broker API.")
                else:
                    print("PASS: Local state matches Broker API.")
        except Exception as e:
            print(f"ERROR: Could not read/update local state: {str(e)}")

    except Exception as e:
        print(f"API ERROR: {str(e)}")

if __name__ == '__main__':
    direct_broker_truth()
