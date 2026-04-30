import sys
import os
import json
import psutil
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.getcwd())

from src.market_data import MStockAPI
from src.trading_config import config
from src.persistence import StateManager

def pre_flight_audit():
    print(f"--- PRE-FLIGHT SYSTEM AUDIT ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ---")
    
    # 1. IP Check
    import requests
    try:
        current_ip = requests.get('https://api.ipify.org').text
        print(f"[IP] Current Public IP: {current_ip}")
    except:
        print("[IP] Failed to fetch public IP")

    # 2. Manifest vs Config Sync
    print("\n[CONFIG] Auditing Neural Manifest Compliance...")
    
    sync_ok = True
    # Check Code Values directly
    if config.first_trade_hard_loss_limit == 2000:
        print("  [OK] 1st Trade Hard SL: 2,000 (CORRECT)")
    else:
        print(f"  [FAIL] 1st Trade Hard SL: {config.first_trade_hard_loss_limit} (NEEDS 2000)")
        sync_ok = False

    if config.win_lock_step == 1000 and config.win_lock_floor_step == 500:
        print("  [OK] Win-Lock: 1000/500 (CORRECT)")
    else:
        print(f"  [FAIL] Win-Lock: {config.win_lock_step}/{config.win_lock_floor_step} (NEEDS 1000/500)")
        sync_ok = False

    expected_tsl = [500.0, 1000.0, 1800.0, 3000.0, 5000.0]
    actual_tsl = [t['threshold'] for t in config.tsl_ladder]
    if all(t in actual_tsl for t in expected_tsl):
        print("  [OK] TSL Ladder: Recovery Mode (CORRECT)")
    else:
        print(f"  [FAIL] TSL Ladder: Mismatch! (Code: {actual_tsl})")
        sync_ok = False

    # 3. Process Check
    print("\n[PROCESS] Checking Bot Services...")
    bot_running = False
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        if proc.info['cmdline'] and 'main.py' in proc.info['cmdline']:
            print(f"  [OK] Trading Bot (main.py) is RUNNING (PID: {proc.info['pid']})")
            bot_running = True
        if proc.info['cmdline'] and 'telegram_bot.py' in proc.info['cmdline']:
            print(f"  [OK] Telegram Control (Sentinel) is RUNNING (PID: {proc.info['pid']})")
    
    if not bot_running:
        print("  [WARN] Trading Bot (main.py) is NOT running.")

    # 4. State Audit
    print("\n[STATE] Auditing Persistence Layer...")
    positions = StateManager.load_positions()
    if not positions:
        print("  [OK] No Zombie Positions found.")
    else:
        print(f"  [WARN] {len(positions)} ACTIVE POSITIONS found.")

    # 5. Data Readiness
    print("\n[DATA] Verifying Indicator Anchors...")
    api = MStockAPI()
    if api.ensure_session_is_valid():
        print("  [OK] MStock API Session: VALID")
        # Check one index for lookback
        # Note: At 08:45 AM, yesterday is the latest bar.
        df = api.get_historical_data("Nifty 50", "NSE", "26000", "day", days=250)
        if df is not None:
            print(f"  [OK] Titan-Shield: Found {len(df)} historical bars.")
            if len(df) >= 250:
                 print("  [OK] Indicator Stability: SECURED (250+ bars)")
            else:
                 print("  [WARN] Indicator Stability: PARTIAL (Wait for YFinance fill)")
        else:
            print("  [FAIL] Titan-Shield: No Data returned.")
    else:
        print("  [FAIL] MStock API Session: INVALID")

    print(f"\n--- AUDIT COMPLETE: {'READY' if sync_ok and bot_running else 'ACTION REQUIRED'} ---")

if __name__ == "__main__":
    pre_flight_audit()
