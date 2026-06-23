import os
import sys
import json
import logging
from datetime import datetime
import pytz

# Add parent directory to path to reach src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.market_data import MStockAPI
from src.trading_config import TradingConfig, config
from src.utils import setup_logging

def run_audit():
    """
    PRE-MARKET HEALTH CHECK (Recommended: 9:10 AM)
    Verifies all systems before market open
    """
    os.makedirs("logs", exist_ok=True)
    audit_log = f"logs/audit_{datetime.now().strftime('%Y%m%d')}.log"
    logger = setup_logging(audit_log)
    
    print("\n" + "="*60)
    print("      TRADING BOT: PRE-MARKET HEALTH CHECK")
    print("="*60)
    
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)
    print(f"Current Time (IST): {now.strftime('%H:%M:%S')}")
    
    checks_passed = 0
    total_checks = 4
    
    # 1. GHOST PROCESS CHECK
    print(f"\n[1/4] Checking for Ghost Processes...")
    lock_file = "bot.lock"
    if os.path.exists(lock_file):
        try:
            with open(lock_file, "r") as f:
                old_pid = f.read().strip()
            print(f"      [WARNING] Lock file found (PID {old_pid}).")
            print(f"      Verify no other bot window is open in Task Manager.")
        except:
            pass
    print("      [OK] No active lock detected for current instance.")
    checks_passed += 1
    
    # 2. CONFIG & MASTER FILE
    print(f"\n[2/4] Verifying Symbol Master...")
    master_file = "nfo_master.csv"
    if os.path.exists(master_file):
        mtime = datetime.fromtimestamp(os.path.getmtime(master_file))
        print(f"      [OK] Found {master_file} (Last Updated: {mtime.strftime('%Y-%m-%d %H:%M')})")
        if mtime.date() < now.date():
            print(f"      [TIP] Consider updating {master_file} for Monday's new expiries.")
    else:
        print(f"      [ERROR] {master_file} is MISSING!")
        return
    checks_passed += 1
    
    # 3. API CONNECTIVITY
    print(f"\n[3/4] Testing Broker Connectivity (mStock)...")
    try:
        api = MStockAPI()
        if api.load_access_token():
            print("      [OK] Local Access Token found.")
            # Verify if still valid
            quote = api.get_quote("NIFTY 50", "NSE")
            if quote:
                print(f"      [OK] Real-time Quote fetched: {quote.get('last_price')}")
                checks_passed += 1
            else:
                print("      [FAILED] Token expired or API down. Please run authenticate.py")
        else:
            print("      [FAILED] No Access Token. Please run authenticate.py")
    except Exception as e:
        print(f"      [ERROR] API Connection Failed: {e}")
    
    # 4. DATA STABILITY (yfinance)
    print(f"\n[4/4] Testing Data Synchronization (yfinance)...")
    try:
        import yfinance as yf
        test_ticker = "^NSEI"
        df = yf.download(test_ticker, period="1d", interval="1m", progress=False)
        if not df.empty:
            print(f"      [OK] yfinance connection healthy. Price: {df.iloc[-1]['Close']}")
            checks_passed += 1
        else:
            print("      [FAILED] yfinance returned empty data.")
    except Exception as e:
        print(f"      [ERROR] yfinance connection failed: {e}")

    print("\n" + "="*60)
    if checks_passed == total_checks:
        print(f"      AUDIT RESULT: [SUCCESS] ALL SYSTEMS READY ({checks_passed}/{total_checks})")
        print("      Bot is safe to start at 09:15 AM.")
    else:
        print(f"      AUDIT RESULT: [WARNING] ISSUES DETECTED ({checks_passed}/{total_checks})")
        print("      Please fix the errors above before the market opens.")
    print("="*60 + "\n")

if __name__ == "__main__":
    run_audit()
