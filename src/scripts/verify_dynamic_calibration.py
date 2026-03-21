from src.market_data import MStockAPI
from main import get_market_data_with_indicators
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

def verify_dynamic_calibration(symbol="SENSEX", exchange="BSE", token="51"):
    api = MStockAPI()
    
    print(f"\n--- VERIFYING DYNAMIC CALIBRATION FOR {symbol} ---")
    
    # 1. Fetch data through the main bot's data engine
    daily_df, intraday_df, spot, vix, is_stable = get_market_data_with_indicators(api, symbol, exchange, token)
    
    if intraday_df is not None:
        print(f"Current Spot: {spot:.2f}")
        print(f"Stability: {'[OK] STABLE' if is_stable else '[BLOCKED] UNSTABLE'}")
        print(f"Last Historical Close: {intraday_df.iloc[-1]['close']:.2f}")
        print(f"Gap (Spot - Hist): {spot - intraday_df.iloc[-1]['close']:.2f}")
        
        # Check Indicators
        hist = intraday_df.iloc[-1]['MACD_Hist']
        print(f"Calibrated MACD Hist: {hist:.2f}")
        
        if abs(spot - intraday_df.iloc[-1]['close']) < 5.0:
            print(f"\nSUCCESS: Dynamic Calibration aligned {symbol} History with Live Spot!")
        else:
            print("\nWARNING: Gap remains significant. Check logs for calibration messages.")
    else:
        print("Data fetch failed. Check connection.")

if __name__ == "__main__":
    verify_dynamic_calibration("SENSEX", "BSE", "51")
    verify_dynamic_calibration("NIFTY 50", "NSE", "26000")
