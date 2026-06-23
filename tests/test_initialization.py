import sys
import os
from unittest.mock import MagicMock, patch

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@patch('src.fno_trading_bot.SymbolMaster')
@patch('src.fno_trading_bot.StateManager')
@patch('src.fno_trading_bot.now_ist')
def test_initialization_without_history(mock_now, mock_state_manager, mock_symbol_master):
    from src.fno_trading_bot import FnOTradingBot
    from src.trading_config import TradingConfig
    
    print("Testing initialization without history...")
    
    # Mock Config
    mock_config = MagicMock(spec=TradingConfig)
    mock_config.initial_capital = 100000.0
    
    # Setup state manager mocks
    mock_state_manager.load_positions.return_value = {}
    mock_state_manager.load_history.return_value = []
    mock_state_manager.load_daily_state.return_value = {}
    
    bot = FnOTradingBot(mock_config)
    
    # Check attributes
    attributes = ['daily_pnl', 'daily_max_pnl', 'daily_trades', 'closed_trades', 'positions']
    for attr in attributes:
        if hasattr(bot, attr):
            print(f"  [OK] Attribute '{attr}' exists (Value: {getattr(bot, attr)})")
        else:
            print(f"  [FAIL] Attribute '{attr}' is MISSING")
            return False
            
    print("Test Passed: All required monitoring attributes are initialized.")
    return True

if __name__ == "__main__":
    if test_initialization_without_history():
        sys.exit(0)
    else:
        sys.exit(1)
