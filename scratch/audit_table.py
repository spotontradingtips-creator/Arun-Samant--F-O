import json
import re

log_file = r"logs\trading_bot_20260504.log"

def analyze():
    with open(log_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    signals = {}
    current_inds = {}
    
    for line in lines:
        # Match Indicator conditions check
        match = re.search(r"OK (.*?): All (.*?) entry conditions met \| RSI=(.*?) \| 15m ADX=(.*?) \| VWAP=(.*)", line)
        if match:
            symbol = match.group(1).strip()
            ttype = match.group(2).strip()
            current_inds[symbol] = {
                'RSI': float(match.group(3).strip()),
                'ADX': float(match.group(4).strip()),
                'VWAP': float(match.group(5).strip()),
                'Type': ttype
            }
            
        # Match Order placement
        order_match = re.search(r"Placing LIVE order: BUY \d+ x (.*?)(CE|PE)", line)
        if order_match:
            contract = order_match.group(1) + order_match.group(2)
            symbol_base = "NIFTY"
            if "BANKNIFTY" in contract: symbol_base = "BANKNIFTY"
            elif "FINNIFTY" in contract: symbol_base = "FINNIFTY"
            elif "SENSEX" in contract: symbol_base = "SENSEX"
            
            if symbol_base in current_inds:
                if contract not in signals:
                    signals[contract] = current_inds[symbol_base]
                current_inds[symbol_base] = {} # Clear it
                
    # Define rules
    def check_rules(ttype, rsi, adx):
        # Base rules: ADX >= 22.0
        adx_pass = adx >= 22.0
        # RSI rules: CE (35-70), PE (35-70)
        rsi_pass = 35.0 <= rsi <= 70.0
        return adx_pass and rsi_pass
        
    print("| Option Contract | Entry Type | RSI Value | 15m ADX | Spot vs VWAP | Rules Met? |")
    print("|-----------------|------------|-----------|---------|--------------|------------|")
    for contract, data in signals.items():
        met = "(PASS) YES" if check_rules(data['Type'], data['RSI'], data['ADX']) else "(FAIL) NO"
        # We don't have exact spot vs vwap in the log regex, but VWAP gate is enforced internally.
        # We will just print the VWAP value.
        print(f"| {contract} | {data['Type']} | {data['RSI']} | {data['ADX']} | {data['VWAP']} | {met} |")

if __name__ == "__main__":
    analyze()
