import re

log_file = "c:\\Antigravity\\Arun Samant - F&O\\logs\\trading_bot_20260506.log"

rejections = {}
try:
    with open(log_file, "r") as f:
        for line in f:
            if "RSI Check Failed" in line or "Momentum Insufficient" in line or "MACD not" in line or "VWAP Guard" in line:
                match = re.search(r"(\w+) \[(CE|PE)\]: (.+)", line)
                if match:
                    symbol = match.group(1)
                    ttype = match.group(2)
                    reason = match.group(3).strip()
                    key = f"{symbol} [{ttype}]"
                    if key not in rejections:
                        rejections[key] = []
                    # Keep track of last few reasons to see what happened late in the day
                    rejections[key].append(reason)
                    
    print("--- DEEP ANALYSIS OF REJECTIONS (LAST 5 ATTEMPTS PER SYMBOL) ---")
    for key, reasons in rejections.items():
        print(f"\n{key}:")
        for r in reasons[-5:]:
            print(f"  - {r}")
except Exception as e:
    print("Error:", e)
