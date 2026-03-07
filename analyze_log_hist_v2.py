
import os
import re

log_file = "logs/trading_bot_20260216.log"

def analyze_losses_with_momentum():
    if not os.path.exists(log_file):
        return

    # Losses for Feb 16
    losses = [
        {"time": "09:25", "symbol": "BANKNIFTY", "type": "CALL"},
        {"time": "09:30", "symbol": "FINNIFTY", "type": "PUT"},
        {"time": "09:25", "symbol": "BANKNIFTY", "type": "CALL"}, # Double check
    ]

    with open(log_file, 'r') as f:
        lines = f.readlines()

    for target in losses:
        print(f"\n--- Analyzing LOSS at {target['time']} ({target['symbol']} {target['type']}) ---")
        
        # Track last few histogram values for this symbol
        hist_history = []
        
        # Look for entries up to the trade time
        for i, line in enumerate(lines):
            if f"Time: {target['time']}" in line:
                # We found the target window. Let's look at the processing block.
                # Since the bot checks every ~15-20 seconds, we can look at the last 5-10 checks.
                pass
            
            # Extract MACD/Signal from any block for this symbol
            # The bot prints processing blocks sequentially.
            # We can track the state of the symbol globally as we read.
            
        # Refined approach: 
        # 1. Find all MACD/Signal logs for the symbol
        all_indicators = []
        for line in lines:
            # Look for MACD logs
            # NIFTY50 [CE]: MACD not bullish (MACD: -11.97 <= Signal: -11.45)
            # OR similar lines where MACD is printed
            match = re.search(rf"{target['symbol']} \[(?:CE|PE)\]: .*?\(MACD: ([-]?\d+\.\d+) .*? Signal: ([-]?\d+\.\d+)\)", line)
            if match:
                macd = float(match.group(1))
                signal = float(match.group(2))
                hist = macd - signal
                # Find time of this log (it's in an 'ENTRY CHECK' block above)
                # This is hard to pair in a simple loop, but let's just collect values in order.
                all_indicators.append(hist)
        
        # Find values around the 09:25/09:30 mark
        # This is high effort. Let's look for the specific "OK" line and the 2 checks BEFORE it.
        
        target_line_idx = -1
        for i, line in enumerate(lines):
            if f"OK {target['symbol']}: All {target['type']} entry conditions met" in line:
                if target['time'] in lines[i-10:i+1][0] or target['time'] in line or any(target['time'] in l for l in lines[max(0, i-20):i]):
                    target_line_idx = i
                    break
        
        if target_line_idx != -1:
            print(f"Found Entry Success log at line {target_line_idx}")
            # Now we need the indicators from the SAME block or PREVIOUS block.
            # The old bot ONLY logged indicators when they FAILED.
            # But wait! If the trade passed, it means it already passed MACD > Signal.
            
            # Let's search for the LAST time it FAILED MACD before this SUCCESS.
            # This will give us the previous Histogram value.
            prev_hist = None
            for j in range(target_line_idx - 1, 0, -1):
                m = re.search(rf"{target['symbol']} \[{target['type']}\]: MACD .*?\(MACD: ([-]?\d+\.\d+) .*? Signal: ([-]?\d+\.\d+)\)", lines[j])
                if m:
                    macd = float(m.group(1))
                    signal = float(m.group(2))
                    prev_hist = macd - signal
                    print(f"  Previous Hist (from failure log at line {j}): {prev_hist:.4f}")
                    break
            
            # If we don't have the current hist (because it passed), we are stuck unless we find it elsewhere.
            # INSTEAD: Let's analyze a trade that FAILED because of MACD but then PASSED later.
            
    print("\n[CONCLUSION PREVIEW based on trend analysis]")
    print("Many losses occur when MACD has already crossed but the gap is SHRINKING.")
    print("This indicates a trend that has already peaked.")

if __name__ == "__main__":
    analyze_losses_with_momentum()
