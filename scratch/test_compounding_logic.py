import sys
import os
from unittest.mock import MagicMock
import pandas as pd

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.fno_trading_bot import FnOTradingBot
from src.trading_config import TradingConfig

def test_compounding_logic():
    print("--- TESTING COMPOUNDING & BUDGETING LOGIC ---")
    
    # 1. Setup Mock API
    mock_api = MagicMock()
    # Mocking Rs 50,000 available funds
    mock_api.get_funds.return_value = 50000.0
    
    # 2. Setup Config
    config = TradingConfig()
    config.initial_capital = 35000.0 # Default in config
    config.daily_loss_limit_pct = 5.0 # 5%
    
    # 3. Initialize Bot
    # This should trigger the API sync and set initial_capital to 50,000
    bot = FnOTradingBot(config, api=mock_api)
    
    print(f"Config Capital: Rs {config.initial_capital}")
    print(f"Bot Initial Capital (Synced): Rs {bot.initial_capital}")
    
    # Verification A: Startup Sync
    if bot.initial_capital == 50000.0:
        print("[OK] Bot successfully synced capital from API at startup.")
    else:
        print("[FAIL] Bot failed to sync capital from API.")
        
    # Verification B: Dynamic Loss Limit
    # 5% of 50,000 should be 2,500
    max_loss = bot.initial_capital * (bot.config.daily_loss_limit_pct / 100.0)
    if max_loss == 2500.0:
        print(f"[OK] Daily Loss Limit correctly scaled to Rs {max_loss}")
    else:
        print(f"[FAIL] Daily Loss Limit scaling failed. Got: {max_loss}")

    # Verification C: Budgeting Logic (High Balance)
    # At Rs 50,000, can we afford Nifty? (Spot 24000 * 0.015 * 75 = 27k)
    # Available (50k) - Reserve (5k) = 45k. Yes.
    can_afford = bot.can_afford_entry("NIFTY", 24000)
    if can_afford:
        print("[OK] Budgeting logic allowed Nifty entry with 50k capital.")
    else:
        print("[FAIL] Budgeting logic blocked Nifty unexpectedly.")

    # Verification D: Budgeting Logic (Low Balance)
    # Now mock lower funds (Rs 20,000)
    mock_api.get_funds.return_value = 20000.0
    # Available (20k) - Reserve (5k) = 15k.
    # Nifty needs 27k. Should fail.
    can_afford_low = bot.can_afford_entry("NIFTY", 24000)
    if not can_afford_low:
        print("[OK] Budgeting logic correctly blocked Nifty entry with low capital (20k).")
    else:
        print("[FAIL] Budgeting logic allowed trade with insufficient funds.")

    # Verification E: Fallback Logic
    mock_api.get_funds.return_value = None # API Error
    bot_fallback = FnOTradingBot(config, api=mock_api)
    if bot_fallback.initial_capital == 35000.0:
        print("[OK] Bot successfully fell back to config capital when API failed.")
    else:
        print(f"[FAIL] Fallback failed. Got: {bot_fallback.initial_capital}")

if __name__ == "__main__":
    test_compounding_logic()
