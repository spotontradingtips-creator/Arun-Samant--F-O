from datetime import time, datetime, timedelta
from src.trading_config import TradingConfig

def test_morning_buffer():
    config = TradingConfig()
    config.market_open = time(9, 15)
    config.morning_buffer_minutes = 15
    config.entry_cutoff = time(15, 15)
    
    # 9:20 AM - Should be BLOCKED
    t1 = time(9, 20)
    res1 = config.can_enter_new_position(t1)
    print(f"9:20 AM allowed? {res1} (Expected: False)")
    
    # 9:30 AM - Should be ALLOWED
    t2 = time(9, 30)
    res2 = config.can_enter_new_position(t2)
    print(f"9:30 AM allowed? {res2} (Expected: True)")
    
    # 9:45 AM - Should be ALLOWED
    t3 = time(9, 45)
    res3 = config.can_enter_new_position(t3)
    print(f"9:45 AM allowed? {res3} (Expected: True)")
    
    # 3:20 PM - Should be BLOCKED (Cutoff)
    t4 = time(15, 20)
    res4 = config.can_enter_new_position(t4)
    print(f"3:20 PM allowed? {res4} (Expected: False)")

if __name__ == '__main__':
    test_morning_buffer()
