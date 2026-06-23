import yfinance as yf
import pandas as pd
import numpy as np

def calculate_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_adx(df, window=14):
    df = df.copy()
    df['up_move'] = df['High'] - df['High'].shift(1)
    df['down_move'] = df['Low'].shift(1) - df['Low']
    
    df['plus_dm'] = np.where((df['up_move'] > df['down_move']) & (df['up_move'] > 0), df['up_move'], 0)
    df['minus_dm'] = np.where((df['down_move'] > df['up_move']) & (df['down_move'] > 0), df['down_move'], 0)
    
    df['tr'] = np.maximum(df['High'] - df['Low'], 
                          np.maximum(abs(df['High'] - df['Close'].shift(1)), 
                                     abs(df['Low'] - df['Close'].shift(1))))
    
    df['atr'] = df['tr'].rolling(window=window).mean()
    df['plus_di'] = 100 * (df['plus_dm'].rolling(window=window).mean() / df['atr'])
    df['minus_di'] = 100 * (df['minus_dm'].rolling(window=window).mean() / df['atr'])
    
    df['dx'] = 100 * abs(df['plus_di'] - df['minus_di']) / (df['plus_di'] + df['minus_di'])
    df['adx'] = df['dx'].rolling(window=window).mean()
    return df['adx']

indices = {
    "NIFTY 50": "^NSEI",
    "BANKNIFTY": "^NSEBANK",
    "SENSEX": "^BSESN"
}

print(f"{'Index':<15} | {'Daily ADX':<10} | {'Current RSI':<10} | {'Last Price':<10}")
print("-" * 55)

for name, symbol in indices.items():
    try:
        # Daily for ADX (250 day lookback)
        df_daily = yf.download(symbol, period="1y", interval="1d", progress=False)
        adx_series = calculate_adx(df_daily)
        adx_val = float(adx_series.iloc[-1])
        
        # 15min for RSI (matching bot logic)
        df_15m = yf.download(symbol, period="5d", interval="15m", progress=False)
        rsi_series = calculate_rsi(df_15m['Close'])
        rsi_val = float(rsi_series.iloc[-1])
        last_price = float(df_15m['Close'].iloc[-1])
        
        print(f"{name:<15} | {adx_val:<10.2f} | {rsi_val:<10.2f} | {last_price:<10.2f}")
    except Exception as e:
        print(f"Error fetching {name}: {e}")
