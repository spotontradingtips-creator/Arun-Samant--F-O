import pandas as pd
from src.market_data import MStockAPI
from src.indicators import TechnicalIndicators
from src.trading_config import TradingConfig

def analyze_failed_trade():
    api = MStockAPI()
    config = TradingConfig()
    
    symbol = 'SENSEX'
    ex, tok, sym = 'BSE', '51', 'SENSEX'
    
    print(f"--- AUTOPSY: SENSEX Trade at 12:30 PM ---")
    
    df, ok = api.get_hybrid_history(sym, ex, tok, '15minute')
    if df is None or df.empty:
        print("Failed to fetch data.")
        return
        
    df['MACD'], df['MACD_Signal'], df['MACD_Hist'] = TechnicalIndicators.calculate_macd(df['close'])
    df['RSI'] = TechnicalIndicators.calculate_rsi(df['close'])
    adx, pdi, mdi = TechnicalIndicators.calculate_adx(df['high'], df['low'], df['close'])
    df['ADX'] = adx
    df['PDI'] = pdi
    df['MDI'] = mdi
    
    # Target time: 2026-04-13 12:30:00+05:30
    target_time = pd.Timestamp("2026-04-13 12:30:00+05:30")
    
    if target_time not in df.index:
         print(f"Target bar {target_time} not found. Using nearest...")
         row_idx = df.index.get_indexer([target_time], method='nearest')[0]
         row = df.iloc[row_idx]
    else:
         row = df.loc[target_time]
    
    print(f"\nTime: {row.name}")
    print(f"Close: {row['close']:.2f}")
    print(f"MACD: {row['MACD']:.2f} | Sig: {row['MACD_Signal']:.2f} | Hist: {row['MACD_Hist']:.2f}")
    print(f"RSI: {row['RSI']:.2f}")
    print(f"ADX: {row['ADX']:.2f} | +DI: {row['PDI']:.2f} | -DI: {row['MDI']:.2f}")
    
    # Check if it met conditions
    hist_prev = df['MACD_Hist'].shift(1).loc[row.name]
    print(f"Prev Hist: {hist_prev:.2f}")
    
    is_dark_green = row['MACD_Hist'] > 10.0 and row['MACD_Hist'] > hist_prev
    print(f"Is Dark Green (>10 & Growing): {is_dark_green}")
    
    is_rsi_safe = 30 < row['RSI'] < 70
    print(f"Is RSI Safe: {is_rsi_safe}")
    
    is_adx_strong = row['ADX'] > 20
    print(f"Is ADX Strong: {is_adx_strong}")

if __name__ == "__main__":
    analyze_failed_trade()
