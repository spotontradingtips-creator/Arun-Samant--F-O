
import os
import re
from datetime import datetime

log_file = "logs/trading_bot_20260216.log"
trades = [
    {"time": "09:22", "symbol": "BANKNIFTY", "type": "CALL", "result": "WIN"},
    {"time": "09:25", "symbol": "BANKNIFTY", "type": "CALL", "result": "LOSS"},
    {"time": "09:30", "symbol": "FINNIFTY", "type": "PUT", "result": "LOSS"},
    {"time": "09:33", "symbol": "FINNIFTY", "type": "CALL", "result": "WIN"},
    {"time": "10:01", "symbol": "BANKNIFTY", "type": "CALL", "result": "WIN"},
]

def analyze_momentum():
    if not os.path.exists(log_file):
        print("Log file not found.")
        return

    print(f"Analyzing trades for {log_file}...")
    
    with open(log_file, 'r') as f:
        content = f.read()

    for trade in trades:
        # Find the entry check block around the time
        # Format: ENTRY CHECK #N | Time: 09:22:27
        pattern = rf"ENTRY CHECK #\d+ \| Time: {trade['time']}:\d+"
        match = re.search(pattern, content)
        
        if match:
            start_pos = match.start()
            # Look at the next 1000 chars for MACD info
            context = content[start_pos:start_pos + 2000]
            
            # Find symbol block
            symbol_pattern = rf"Processing {trade['symbol']}.*?(?=Processing|$)"
            symbol_match = re.search(symbol_pattern, context, re.DOTALL)
            
            if symbol_match:
                symbol_context = symbol_match.group(0)
                # Look for MACD logs: (MACD: -54.61 <= Signal: -41.57)
                macd_pattern = r"MACD: ([-]?\d+\.\d+) .*? Signal: ([-]?\d+\.\d+)"
                macd_match = re.search(macd_pattern, symbol_context)
                
                if macd_match:
                    macd = float(macd_match.group(1))
                    signal = float(macd_match.group(2))
                    hist = macd - signal
                    
                    # To check if it was "increasing", we need the PREVIOUS check's values
                    # This script is a bit simple, but let's see what we get for Histogram state.
                    print(f"\nTrade at {trade['time']} ({trade['symbol']} {trade['type']}):")
                    print(f"  Result: {trade['result']}")
                    print(f"  MACD: {macd}, Signal: {signal} => HIST: {hist:.4f}")
                    
                    if trade['type'] == "CALL":
                        if hist <= 0:
                            print("  >>> WOULD HAVE BEEN FILTERED (Hist <= 0)")
                        else:
                            print("  >>> POTENTIAL PASS (Need momentum check)")
                    else:
                        if hist >= 0:
                            print("  >>> WOULD HAVE BEEN FILTERED (Hist >= 0)")
                        else:
                            print("  >>> POTENTIAL PASS (Need momentum check)")
                else:
                    # If it passed all conditions, it logged the "OK" line which doesn't have MACD
                    print(f"\nTrade at {trade['time']} ({trade['symbol']} {trade['type']}):")
                    print(f"  Status: OK line found, but MACD details not logged on success in old version.")
            else:
                print(f"No processing block for {trade['symbol']} at {trade['time']}")
        else:
            print(f"No log entry found for {trade['time']}")

if __name__ == "__main__":
    analyze_momentum()
