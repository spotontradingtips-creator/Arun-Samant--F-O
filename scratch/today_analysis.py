import json

with open(r'c:\Antigravity\Arun Samant - F&O\data\daily_history.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

today = "2026-05-05"
todays_trades = [t for t in data if t.get('entry_time', '').startswith(today)]

print("Completed Trades:")
for t in todays_trades:
    print(f"[{t['trade_type']}] {t['underlying']} - {t['option_symbol']}")
    print(f"  Entry Time: {t['entry_time']} | Exit Time: {t['exit_time']}")
    print(f"  PNL: Rs {t.get('pnl', 0):.2f} ({t.get('pnl_percentage', 0):.2f}%)")
    print(f"  Exit Reason: {t.get('exit_reason', 'Unknown')}")
    print("-" * 40)

try:
    with open(r'c:\Antigravity\Arun Samant - F&O\data\daily_state.json', 'r', encoding='utf-8') as f:
        daily_state = json.load(f)
    print("\nDaily State:")
    print(f"  Date: {daily_state.get('date')}")
    print(f"  Daily PNL: Rs {daily_state.get('daily_pnl', 0):.2f}")
    print(f"  Max PNL Reached: Rs {daily_state.get('daily_max_pnl', 0):.2f}")
except Exception as e:
    print("Could not load daily_state.json")

try:
    with open(r'c:\Antigravity\Arun Samant - F&O\data\positions.json', 'r', encoding='utf-8') as f:
        positions = json.load(f)
    print("\nOpen Positions:")
    for k, v in positions.items():
        print(f"[{v['trade_type']}] {v['underlying']} - {v['option_symbol']}")
        print(f"  Entry Time: {v['entry_time']}")
except Exception as e:
    print("Could not load positions.json")
