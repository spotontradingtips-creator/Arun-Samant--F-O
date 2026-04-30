import json
import re

history_file = r'c:\Antigravity\Arun Samant - F&O\data\daily_history.json'
log_file = r'c:\Antigravity\Arun Samant - F&O\logs\trading_bot_20260429.log'

print('--- Searching JSON ---')
try:
    with open(history_file, 'r') as f:
        data = json.load(f)
    for t in data:
        if '2026-04-29' in t.get('entry_time', ''):
            print(f"ID: {t.get('position_id')} | PnL: {t.get('pnl')} | Reason: {t.get('exit_reason')} | MaxPnL: {t.get('max_pnl_reached')} | Peak SL: {t.get('dynamic_trailing_sl')}")
except Exception as e:
    print('JSON error:', e)

print('\n--- Searching Log File for exact numbers ---')
try:
    with open(log_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for line in lines:
        if '3487' in line or '455' in line or '282' in line or '3487.25' in line:
            if 'P&L' in line or 'profit' in line.lower() or 'loss' in line.lower() or 'EXIT' in line:
                print(line.strip())
except Exception as e:
    print('Log error:', e)
