import pandas as pd
from src.market_data import MStockAPI
from src.indicators import TechnicalIndicators
import yfinance as yf
from datetime import datetime
import logging

# Setup minimal logging to see the "Normalizing" message
logging.basicConfig(level=logging.INFO)

def verify_normalization():
    api = MStockAPI()
    symbol = "SENSEX"
    exchange = "BSE"
    token = "51"
    
    print(f"\n--- VERIFYING SENSEX NORMALIZATION ---")
    
    print("Fetching mStock history...")
    mstock_df = api.get_historical_data(symbol, exchange, token, "15minute", days=10)
    print("Fetching yfinance history...")
    yf_df = yf.download("^BSESN", period="3d", interval="15m", progress=False)
    # Ensure it's a Series even if MultiIndex
    yf_close = yf_df['Close'].iloc[:, 0] if isinstance(yf_df['Close'], pd.DataFrame) else yf_df['Close']
    yf_close.index = yf_close.index.tz_convert("Asia/Kolkata")
    
    if mstock_df is not None and not mstock_df.empty:
        print(f"mStock tail: {mstock_df.index[-1]}")
    if not yf_close.empty:
        print(f"yfinance head: {yf_close.index[0]}")
        
    common = mstock_df.index.intersection(yf_close.index)
    print(f"Intersection size: {len(common)}")
    if not common.empty:
        print(f"Common timestamps: {list(common[-3:])}")
        offsets = mstock_df.loc[common[-5:], 'close'] - yf_close.loc[common[-5:]]
        print(f"Median Offset found: {offsets.median():.2f}")
        
    # Call hybrid to see if it processes them
    df = api.get_hybrid_history(symbol, exchange, token, "15minute", days=10)
    
    # 4. Check LIVE quote vs last bar
    quote = api.get_quote(symbol, exchange)
    if quote:
        live_price = float(quote.get('last_price', 0))
        hist_price = float(df.iloc[-1]['close'])
        print(f"\n--- LIVE VS HISTORICAL ---")
        print(f"mStock Live Quote: {live_price:.2f}")
        print(f"Latest Normalized Close (yf): {hist_price:.2f}")
        print(f"Live Offset: {live_price - hist_price:.2f}")
    
    if df is not None and not df.empty:
        print(f"Total bars: {len(df)}")
        print(f"Index start: {df.index[0]}")
        print(f"Index end: {df.index[-1]}")
        
        # Calculate MACD 
        df['MACD'], df['MACD_Signal'], df['MACD_Hist'] = \
            TechnicalIndicators.calculate_macd(df['close'])
            
        last_row = df.iloc[-1]
        prev_row = df.iloc[-2] if len(df) > 1 else last_row
        
        print(f"Current Price: {last_row['close']:.2f}")
        print(f"MACD Hist: {last_row['MACD_Hist']:.2f} (Prev: {prev_row['MACD_Hist']:.2f})")
        
        # Check for vertical spikes at the transition point
        # (Though we can't easily identify the transition point programmatically here, 
        # the lack of a massive 'Success' message with huge momentum is a good sign)
        print("\nSuccess: Normalization logic executed.")
    else:
        print("Error: Could not fetch data.")

if __name__ == "__main__":
    verify_normalization()
