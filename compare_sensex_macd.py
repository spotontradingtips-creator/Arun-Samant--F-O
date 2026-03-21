import pandas as pd
import yfinance as yf
from src.market_data import MStockAPI
from src.indicators import TechnicalIndicators
from datetime import datetime
import pytz

def compare_sensex_data():
    api = MStockAPI()
    symbol = "SENSEX"
    exchange = "BSE"
    token = "51"
    
    # 1. Fetch mStock history (pure)
    mstock_df = api.get_historical_data(symbol, exchange, token, "15minute", days=10)
    
    # 2. Fetch yfinance history (pure)
    yf_df = yf.download("^BSESN", period="10d", interval="15m", progress=False)
    # Ensure it's a Series even if MultiIndex
    yf_close = yf_df['Close'].iloc[:, 0] if isinstance(yf_df['Close'], pd.DataFrame) else yf_df['Close']
    
    if mstock_df is not None and not mstock_df.empty:
        print(f"mStock trailing timestamps: {list(mstock_df.index[-3:])}")
    if not yf_close.empty:
        print(f"yfinance trailing timestamps: {list(yf_close.index[-3:])}")

    if mstock_df is not None and not mstock_df.empty:
        # Convert mstock index to tz-aware to match yfinance
        if mstock_df.index.tz is None:
            mstock_df.index = mstock_df.index.tz_localize("Asia/Kolkata")
            
        common_times = mstock_df.index.intersection(yf_close.index.tz_convert("Asia/Kolkata"))
        
        if not common_times.empty:
            print("\n--- PRICE OFFSET COMPARISON ---")
            for t in common_times[-5:]:
                ms_price = mstock_df.loc[t, 'close']
                # Correct UTC handling
                utc_time = t.tz_convert("UTC")
                yf_price = float(yf_close.loc[utc_time]) 
                offset = ms_price - yf_price
                print(f"Time: {t} | mStock: {ms_price:.2f} | yf: {yf_price:.2f} | Offset: {offset:.2f}")
        else:
            print("\nNo common timestamps found.")
    else:
        print("\nmStock returned no historical data for SENSEX.")

if __name__ == "__main__":
    compare_sensex_data()
