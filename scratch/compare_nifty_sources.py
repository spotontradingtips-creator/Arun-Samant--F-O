
import sys
import os
import pandas as pd
import yfinance as yf
from datetime import datetime

# Add src to path
sys.path.insert(0, os.getcwd())

from src.market_data import MStockAPI
from src.indicators import TechnicalIndicators

def compare_sources():
    api = MStockAPI()
    
    # Symbols to test
    indices = [
        {"name": "NIFTY", "broker_sym": "Nifty 50", "token": "26000", "ticker": "^NSEI"},
        {"name": "BANKNIFTY", "broker_sym": "NIFTY BANK", "token": "26009", "ticker": "^NSEBANK"}
    ]
    
    print(f"DATA SOURCE COMPARISON | Time: {datetime.now()}")
    print("-" * 80)
    
    for item in indices:
        name = item["name"]
        broker_sym = item["broker_sym"]
        exch = "NSE"
        token = item["token"]
        ticker = item["ticker"]
        
        print(f"\n--- {name} ---")
        # 1. Broker Data (mStock)
        df_broker = api.get_historical_data(broker_sym, exch, token, "day", days=250)
        adx_broker, _, _ = TechnicalIndicators.calculate_adx(df_broker['high'], df_broker['low'], df_broker['close'])
        
        # 2. YFinance Data
        df_yf = yf.download(ticker, period="2y", interval="1d", progress=False)
    if isinstance(df_yf.columns, pd.MultiIndex):
        df_yf.columns = [col[0] for col in df_yf.columns]
    df_yf = df_yf.rename(columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close'})
    adx_yf, _, _ = TechnicalIndicators.calculate_adx(df_yf['high'], df_yf['low'], df_yf['close'])
    
    print(f"Latest Dates:")
    print(f"  Broker: {df_broker.index[-1]}")
    print(f"  YFinance: {df_yf.index[-1]}")
    print(f"\nADX Values:")
    print(f"  Broker (mStock): {adx_broker.iloc[-1]:.2f}")
    print(f"  YFinance (^NSEI): {adx_yf.iloc[-1]:.2f}")
    
    # Compare OHLC of last common date
    common_date = df_broker.index[-1]
    if common_date in df_yf.index:
        print(f"\nOHLC Comparison for {common_date.date()}:")
        print(f"  Broker: O:{df_broker.loc[common_date, 'open']:.2f} H:{df_broker.loc[common_date, 'high']:.2f} L:{df_broker.loc[common_date, 'low']:.2f} C:{df_broker.loc[common_date, 'close']:.2f}")
        print(f"  YFinance: O:{df_yf.loc[common_date, 'open']:.2f} H:{df_yf.loc[common_date, 'high']:.2f} L:{df_yf.loc[common_date, 'low']:.2f} C:{df_yf.loc[common_date, 'close']:.2f}")

if __name__ == "__main__":
    compare_sources()
