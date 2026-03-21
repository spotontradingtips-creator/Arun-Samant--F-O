import pandas as pd
import yfinance as yf
from src.market_data import MStockAPI
from datetime import datetime, timedelta
import pytz

def check_mstock_consistency():
    api = MStockAPI()
    symbol = "SENSEX"
    exchange = "BSE"
    token = "51"
    
    print(f"Checking consistency for {symbol}...")
    
    # 1. Get Live Quote for SENSEX
    symbol = "SENSEX"
    exchange = "BSE"
    token = "51"
    quote_sym = api.get_quote(symbol, exchange)
    live_price = quote_sym.get('last_price', 0)
    print(f"mStock {symbol} Live Price: {live_price}")
    
    # 2. Get yfinance 1m history
    yf_df = yf.download("^BSESN", period="1d", interval="1m", progress=False)
    if not yf_df.empty:
        yf_close = yf_df['Close'].iloc[:, 0] if isinstance(yf_df['Close'], pd.DataFrame) else yf_df['Close']
        last_yf = yf_close.iloc[-1]
        last_time = yf_close.index[-1].tz_convert("Asia/Kolkata")
        print(f"yfinance 1m Last Bar ({last_time}): {last_yf:.2f}")
        
        dynamic_offset = live_price - last_yf
        print(f"Current Dynamic Offset: {dynamic_offset:.2f}")
        
        # Test if this offset makes sense by checking previous bars
        if len(yf_close) > 5:
            prev_yf = yf_close.iloc[-5]
            print(f"yfinance 5m ago: {prev_yf:.2f} -> Calibrated: {prev_yf + dynamic_offset:.2f}")
    print(f"mStock Live Quote: {live_price}")
    
    # 2. Get mStock 1-minute history for today
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)
    df_1m = api.get_historical_data(symbol, exchange, token, "1minute", days=1)
    
    if df_1m is not None and not df_1m.empty:
        last_bar = df_1m.iloc[-1]
        print(f"mStock 1m History Last Bar ({df_1m.index[-1]}): {last_bar['close']}")
        print(f"Difference (Live - Hist): {live_price - last_bar['close']:.2f}")
    else:
        print("mStock returned no 1m history for today.")

    # 3. Get yfinance 1m history
    yf_df = yf.download("^BSESN", period="1d", interval="1m", progress=False)
    if not yf_df.empty:
        yf_close = yf_df['Close'].iloc[:, 0] if isinstance(yf_df['Close'], pd.DataFrame) else yf_df['Close']
        last_yf = yf_close.iloc[-1]
        print(f"yfinance 1m History Last Bar ({yf_close.index[-1]}): {last_yf}")
        print(f"Difference (Live - yf): {live_price - last_yf:.2f}")

if __name__ == "__main__":
    check_mstock_consistency()
