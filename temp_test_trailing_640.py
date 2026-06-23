import sys, os
project_path = r'c:\\Antigravity\\Arun Samant - F&O'
sys.path.append(project_path)

from src.trading_models import Position, TradeType
from src.fno_trading_bot import FnOTradingBot
from src.trading_config import TradingConfig

class DummyConfig(TradingConfig):
    def __init__(self):
        self.initial_capital = 1000000
        self.win_lock_enabled = False
        self.profit_target_amount = 2000
        self.max_premium_loss_percent = -50.0
        self.daily_loss_limit_pct = 5.0
        self.vix_min_threshold = 10.0
        self.rsi_min = 30
        self.rsi_max = 65
        self.rsi_pe_min = 35
        self.rsi_pe_max = 75
        self.adx_daily_min = 25.0
        self.win_lock_step = 250.0
        self.win_lock_floor_step = 150.0
        self.strike_depth = 1
        self.default_num_lots = 1
        self.lot_sizes = {'NIFTY50': 75, 'BANKNIFTY': 25}
    def can_enter_new_position(self, now):
        return True
    def get_sl_percentage(self, underlying, vix):
        return 0.7
    def get_lot_size(self, underlying):
        return self.lot_sizes.get(underlying, 75)

dummy_cfg = DummyConfig()
bot = FnOTradingBot(dummy_cfg)

pos = Position(
    position_id='test640',
    underlying='NIFTY50',
    trade_type=TradeType.CE,
    entry_time=None,
    entry_price=100.0,
    entry_underlying_price=15000.0,
    lot_size=1,
    sl_percentage=0.7,
    vix_at_entry=15,
    macd_entry_idx=0,
    option_symbol=None,
    strike_price=15000.0
)

# Simulate profit reaching 640
pos.max_pnl_reached = 640.0
current_premium = pos.entry_price + (pos.max_pnl_reached / pos.lot_size)
exit_reason = bot.check_exit_conditions(pos, current_premium, 15000.0, 0, None)
print('Dynamic trailing SL after 640 P&L:', pos.dynamic_trailing_sl)
print('Exit reason:', exit_reason)
