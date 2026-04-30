import os
import json
import sys
import pandas as pd
from datetime import datetime

# Add root to path
root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, root)

class AuditLogger:
    def info(self, msg): print(f"[\033[94mINFO\033[0m] {msg}")
    def success(self, msg): print(f"[\033[92mPASS\033[0m] {msg}")
    def error(self, msg): print(f"[\033[91mFAIL\033[0m] {msg}")
    def warn(self, msg): print(f"[\033[93mWARN\033[0m] {msg}")

log = AuditLogger()

def run_audit():
    print("\n" + "="*50)
    print("   SENTINEL HUB - PRE-FLIGHT SYSTEM AUDIT   ")
    print("="*50 + "\n")
    
    # 1. Credentials Check
    if os.path.exists('credentials.json'):
        try:
            with open('credentials.json', 'r', encoding='utf-8') as f:
                creds = json.load(f)
                if creds.get('mstock', {}).get('access_token'):
                    log.success("API Token Found")
                else: log.error("API Token Missing in credentials.json")
        except: log.error("credentials.json is corrupted")
    else: log.error("credentials.json not found")

    # [NEW] 1b. IP Verification (Rule 87)
    registered_ip = "49.37.133.14"
    try:
        import requests
        curr_ip = requests.get("https://api.ipify.org", timeout=5).text
        if curr_ip == registered_ip:
            log.success(f"IP Verification: Correct ({curr_ip})")
        else:
            log.warn(f"IP Mismatch: Current {curr_ip} vs Registered {registered_ip}. UPDATE MSTOCK PORTAL!")
    except Exception as e:
        log.warn(f"IP Verification skipped: {e}")

    # 2. Logic Integrity Check (Exhaustive Rule Scan)
    print("--- [Deep Logic Scan] ---")
    
    # 2a. Confirmed Candle Rule (Safety Shield)
    if os.path.exists('src/fno_trading_bot.py'):
        with open('src/fno_trading_bot.py', 'r', encoding='utf-8') as f:
            bot_content = f.read()
            # Rule 5 check: Closed 15-minute candle verification
            if "check_idx = current_row_idx - 1" in bot_content:
                log.success("Exit: Confirmed Candle Rule (Safety Shield) - ENABLED")
            else:
                log.error("Exit: Confirmed Candle Rule - DISABLED/MISSING")

    if os.path.exists('main.py'):
        with open('main.py', 'r', encoding='utf-8') as f:
            main_content = f.read()
            # Check for multi-index processing (Corrected names for Turbo version)
            indices = ["NIFTY", "BANKNIFTY", "SENSEX"]
            missing_indices = [idx for idx in indices if idx not in main_content]
            if not missing_indices:
                log.success(f"Indices: All 3 Turbo indices processed ({', '.join(indices)})")
            else:
                log.error(f"Indices: Missing processing for {missing_indices}")

    # 2b. Entry Rules (Conditions)
    rules = {}
    if os.path.exists('src/fno_trading_bot.py'):
        with open('src/fno_trading_bot.py', 'r', encoding='utf-8') as f:
            bot_code = f.read()
            
            # VIX Verification
            if "if vix < self.config.vix_min_threshold:" in bot_code:
                log.success("Entry: VIX Floor Check - ACTIVE")
                rules['VIX Min'] = "12.0"
            else: log.error("Entry: VIX Floor Check - MISSING")
            
            # RSI Verification
            if "self.config.rsi_min <= rsi <= self.config.rsi_max" in bot_code:
                log.success("Entry: RSI Safety Zone - ACTIVE")
                rules['RSI Range'] = "30 - 70"
            else: log.error("Entry: RSI Safety Zone - MISSING")
            
            # Daily ADX Verification
            if "daily_adx <= self.config.adx_daily_min" in bot_code:
                log.success("Entry: Daily ADX Trend Check - ACTIVE")
                rules['Daily ADX Min'] = "22.0"
            else: log.error("Entry: Daily ADX Check - MISSING")

            # Win-Lock Logic (Rule 3)
            if "self.get_win_lock_floor()" in bot_code:
                log.success("Entry: Global Win-Lock Protection - ACTIVE")
                rules['Profit Cap'] = "UNCAPPED (Win-Lock Active)"
            else: log.warn("Entry: Global Win-Lock Protection - MISSING")

            # Anti-Duplication Verification
            if "Avoiding Duplicate Strike" in bot_code:
                log.success("Entry: Anti-Duplication Protection - ACTIVE")
            else: log.error("Entry: Anti-Duplication - MISSING")

    # 2c. Exit Rules Verification
    if os.path.exists('src/fno_trading_bot.py'):
        with open('src/fno_trading_bot.py', 'r', encoding='utf-8') as f:
            bot_code = f.read()
            # Profit Target Verification
            if "profit_target_amount" in bot_code:
                log.success("Exit: Profit Target Detection - ACTIVE")
                rules['Profit Target'] = "Rs 2000.0"
            else: log.error("Exit: Profit Target Detection - MISSING")
            
            # Safety Net
            if "pnl_pct <= max_premium_loss" in bot_code:
                log.success("Exit: -50.0% Safety Net - ACTIVE")
                rules['Safety Net'] = "-50.0%"

    # 1. Trading Windows
    print("  [Trading Window]")
    print("  Market Open.............. : 09:15 AM")
    print("  Entry Cutoff............. : 03:25 PM")
    print("  Market Close............. : 03:30 PM")
    
    # 2. Risk Management
    print("\n  [Risk Parameters]")
    try:
        if os.path.exists('config.json'):
            with open('config.json', 'r', encoding='utf-8') as f:
                cfg = json.load(f)
                pt = cfg.get('profit_targets', {}).get('profit_target_amount', 2000.0)
                pl = cfg.get('daily_win_lock', {}).get('step_amount', 500.0)
                print(f"  Single Trade Target...... : Rs {pt}")
                print(f"  Win-Lock Step............ : Rs {pl}")
                
                # Audit TSL Ladder
                tsl = cfg.get('tsl_ladder', [])
                if len(tsl) >= 6:
                    log.success("TSL Ladder: Stages 1-6 Confirmed (Neural Manifest)")
                else:
                    log.warn(f"TSL Ladder: Only {len(tsl)} stages found (Expected 6)")
        else:
            print(f"  Profit Target............ : {rules.get('Profit Target', 'Rs 2000.0')}")
            print(f"  Win-Lock................. : Rs 500.0")
    except:
        print(f"  Profit Target............ : {rules.get('Profit Target', 'Rs 2000.0')}")
    print(f"  Safety Net (Premium)..... : {rules.get('Safety Net', '-50.0%')}")
    print("  Stop Loss (NIFTY)........ : 0.70% (Spot)")
    print("  Stop Loss (BANKNIFTY).... : 1.20% (Spot)")
    print("  Stop Loss (SENSEX)....... : 1.00% (Spot)")
    
    # 3. Strategy Conditions
    print("\n  [Strategy Rules]")
    print(f"  VIX Min Floor............ : {rules.get('VIX Min', '10.0')}")
    print(f"  RSI Range................ : {rules.get('RSI Range', '30 - 70')}")
    print(f"  Daily ADX Min............ : {rules.get('Daily ADX Min', '30.0')}")
    print("  Analysis Timeframe....... : 15 Minutes")
    print("  Strike Selection......... : ATM (Depth 0)")
    
    # 4. Indicators Configuration
    print("\n  [Indicator Setup]")
    print("  MACD Periods............. : 12, 26, 9")
    print("  RSI Period............... : 14")
    print("  ADX Period............... : 14")

    # 5. Position Sizing
    print("\n  [Lot Sizes]")
    print("  NIFTY.................... : 65 Qty (Custom)")
    print("  BANKNIFTY................ : 30 Qty")
    print("  SENSEX................... : 20 Qty")

    # 3. Data Integrity (Positions)
    print("\n--- [State Verification] ---")
    if os.path.exists('data/positions.json'):
        try:
            with open('data/positions.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                if len(data) == 0:
                    log.success("State Clean: No ghost positions")
                else:
                    log.warn(f"Ghost Positions Found: {list(data.keys())} - Reconcile if manual exit occurred.")
        except: log.error("data/positions.json is corrupted")

    # 4. Config sanity
    if os.path.exists('config.json'):
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                cfg = json.load(f)
                log.success(f"Config Loaded: Profit Target @ {cfg.get('profit_targets', {}).get('profit_target_amount', 'N/A')}")
        except: log.error("config.json is corrupted")

    print("\n" + "="*50)
    print("        AUDIT COMPLETE - FLY SAFE         ")
    print("="*50 + "\n")

if __name__ == "__main__":
    run_audit()
