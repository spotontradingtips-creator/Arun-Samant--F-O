import re
import json

log_file = r"logs\trading_bot_20260504.log"

def analyze_full():
    with open(log_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    trades = []
    
    # We will scan through and build a state machine for each symbol
    state = {}
    
    for line in lines:
        # Match symbol from lines like "BANKNIFTY [PE]: First Trade - Trend Active..."
        m_trend = re.search(r"([A-Z]+) \[(CE|PE)\]: (First Trade|Subsequent Trade) - Trend Active", line)
        if m_trend:
            sym, typ = m_trend.group(1), m_trend.group(2)
            if sym not in state: state[sym] = {}
            state[sym]['MACD_Signal'] = "Pass (Trend Active)"
            state[sym]['Type'] = typ
            
        m_mom = re.search(r"([A-Z]+) \[(CE|PE)\]: MACD Histogram Hunter Momentum Active", line)
        if m_mom:
            sym, typ = m_mom.group(1), m_mom.group(2)
            if sym not in state: state[sym] = {}
            state[sym]['MACD_Jump'] = "Pass (Momentum Active)"
            
        m_ok = re.search(r"OK (.*?): All (.*?) entry conditions met \| RSI=(.*?) \| 15m ADX=(.*?) \| VWAP=(.*)", line)
        if m_ok:
            sym = m_ok.group(1).strip()
            typ = m_ok.group(2).strip()
            rsi = m_ok.group(3).strip()
            adx = m_ok.group(4).strip()
            vwap = m_ok.group(5).strip()
            
            if sym not in state: state[sym] = {}
            state[sym]['RSI'] = rsi
            state[sym]['ADX'] = adx
            state[sym]['VWAP'] = vwap
            
        m_order = re.search(r"Placing LIVE order: BUY \d+ x (.*?)(CE|PE)", line)
        if m_order:
            contract = m_order.group(1) + m_order.group(2)
            
            sym = "NIFTY"
            if "BANKNIFTY" in contract: sym = "BANKNIFTY"
            elif "FINNIFTY" in contract: sym = "FINNIFTY"
            elif "SENSEX" in contract: sym = "SENSEX"
            
            if sym in state and 'RSI' in state[sym]:
                # We have a full trade!
                # Only add if it's a unique contract
                if not any(t['Contract'] == contract for t in trades):
                    trades.append({
                        'Contract': contract,
                        'Type': state[sym].get('Type', typ),
                        'MACD_Trend': state[sym].get('MACD_Signal', 'Fail/Unknown'),
                        'MACD_Jump': state[sym].get('MACD_Jump', 'Fail/Unknown'),
                        'RSI': state[sym].get('RSI', 'N/A'),
                        'ADX': state[sym].get('ADX', 'N/A'),
                        'VWAP': state[sym].get('VWAP', 'N/A')
                    })
                # Clear state
                state[sym] = {}

    print("| Contract | Type | MACD Trend | MACD Jump | RSI Level | 15m ADX | Spot vs VWAP |")
    print("|---|---|---|---|---|---|---|")
    for t in trades:
        print(f"| {t['Contract']} | {t['Type']} | {t['MACD_Trend']} | {t['MACD_Jump']} | {t['RSI']} | {t['ADX']} | {t['VWAP']} |")

if __name__ == "__main__":
    analyze_full()
