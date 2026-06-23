import re
import json
import os

log_file = r"logs\trading_bot_20260504.log"
orders_file = r"logs\orders_log.json"

def audit():
    trades = []
    current_indicators = {}
    
    if not os.path.exists(log_file):
        print("Log file not found.")
        return
        
    with open(log_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for line in lines:
        # Match indicator values
        # Example: OK NIFTY: All PE entry conditions met | RSI=42.1 | 15m ADX=25.6 | VWAP=24500.5
        match = re.search(r"OK (.*?): All (.*?) entry conditions met \| RSI=(.*?) \| 15m ADX=(.*?) \| VWAP=(.*)", line)
        if match:
            symbol = match.group(1).strip()
            trade_type = match.group(2).strip()
            rsi = match.group(3).strip()
            adx = match.group(4).strip()
            vwap = match.group(5).strip()
            current_indicators[symbol] = {
                'rsi': rsi,
                'adx': adx,
                'vwap': vwap,
                'type': trade_type
            }
            
        # Match Order Placement
        # Example: Placing LIVE order: BUY 30 x BANKNIFTY26MAY55300CE
        order_match = re.search(r"Placing LIVE order: BUY \d+ x (.*?)(CE|PE)", line)
        if order_match:
            contract = order_match.group(1) + order_match.group(2)
            symbol_base = "NIFTY"
            if "BANKNIFTY" in contract: symbol_base = "BANKNIFTY"
            elif "FINNIFTY" in contract: symbol_base = "FINNIFTY"
            elif "SENSEX" in contract: symbol_base = "SENSEX"
            
            inds = current_indicators.get(symbol_base, {})
            trades.append({
                'contract': contract,
                'rsi': inds.get('rsi', 'N/A'),
                'adx': inds.get('adx', 'N/A'),
                'vwap': inds.get('vwap', 'N/A'),
                'type': inds.get('type', 'N/A')
            })
            # Clear it so we don't reuse it accidentally
            current_indicators[symbol_base] = {}

    print(json.dumps(trades, indent=2))

if __name__ == "__main__":
    audit()
