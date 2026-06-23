import yfinance as yf
import pandas as pd
import pandas_ta as ta

def check_adx(ticker, name):
    print(f"Checking {name} ({ticker})...")
    data = yf.download(ticker, period="1y", interval="1d", progress=False)
    if data.empty:
        print(f"No data for {name}")
        return
    
    # Ensure column names are correct (yfinance might return multi-index or just Single)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    
    # Calculate ADX
    adx_df = data.ta.adx(length=14)
    if adx_df is not None and not adx_df.empty:
        # Columns are typically ADX_14, DMP_14, DMN_14
        current_adx = adx_df.iloc[-1, 0] # First column is ADX
        print(f"Current Daily ADX for {name}: {current_adx:.2f}")
    else:
        print(f"ADX calculation failed for {name}")

indices = [
    ("^NSEI", "NIFTY"),
    ("^NSEBANK", "BANKNIFTY"),
    ("^BSESN", "SENSEX")
]

for ticker, name in indices:
    check_adx(ticker, name)
