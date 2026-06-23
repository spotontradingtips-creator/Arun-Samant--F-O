
import pandas as pd
import numpy as np
import os
import sys
from datetime import datetime

# Add src to path to use bot's indicators
sys.path.append(os.getcwd())
from src.indicators import TechnicalIndicators

def run_audit(symbol, file_path):
    print(f"\n--- AUDITING {symbol} ---")
    df = pd.read_csv(file_path, index_col=0, parse_dates=True)
    if df.empty:
        print(f"No data found for {symbol}")
        return

    # Calculate Indicators
    # 1. 15m Indicators
    df['MACD'], df['MACD_Signal'], df['MACD_Hist'] = TechnicalIndicators.calculate_macd(df['Close'])
    df['RSI'] = TechnicalIndicators.calculate_rsi(df['Close'])
    df['ADX'], df['+DI'], df['-DI'] = TechnicalIndicators.calculate_adx(df['High'], df['Low'], df['Close'])
    
    # Hunter Parameters
    MACD_JUMP_THRESHOLD = 2.0
    ADX_MIN = 30.0
    RSI_CE_MAX = 70.0
    RSI_PE_MAX = 70.0
    
    missed_trades = []
    
    # Iterate through today's bars (April 20, 2026)
    today = "2026-04-20"
    today_df = df[df.index.strftime('%Y-%m-%d') == today]
    
    if today_df.empty:
        print(f"No today's data found in {file_path}")
        return

    # Previous Hist for Jump calculation init
    prev_hist = None
    prev_rsi = None
    
    # To properly calculate ADX Daily/Long-term, we use the 15m ADX as a proxy for trend strength
    # or look at the last available daily value.
    
    for idx, row in today_df.iterrows():
        # Find index in full df to get previous values
        full_idx = df.index.get_loc(idx)
        if full_idx < 1: continue
        
        prev_row = df.iloc[full_idx - 1]
        
        hist = row['MACD_Hist']
        p_hist = prev_row['MACD_Hist']
        macd = row['MACD']
        sig = row['MACD_Signal']
        rsi = row['RSI']
        p_rsi = prev_row['RSI']
        adx = row['ADX']
        
        # --- CE SIGNAL ---
        ce_signal = False
        ce_reason = ""
        
        # Mandatory 1: MACD Bullish
        if macd > sig:
            # Mandatory 2: Momentum Jump
            jump = hist - p_hist
            if jump >= MACD_JUMP_THRESHOLD:
                # Mandatory 3: RSI Flow
                if rsi > p_rsi and rsi <= RSI_CE_MAX:
                    # Mandatory 4: ADX Trend
                    if adx >= ADX_MIN:
                        ce_signal = True
                    else:
                        ce_reason = f"ADX too low ({adx:.2f})"
                else:
                    ce_reason = f"RSI Flow/Cap (RSI: {rsi:.2f}, Prev: {p_rsi:.2f})"
            else:
                ce_reason = f"MACD Jump low ({jump:.2f})"
        
        if ce_signal:
            missed_trades.append({"Time": idx, "Type": "CE", "RSI": rsi, "MACD_Hist": hist, "Jump": hist - p_hist, "ADX": adx})

        # --- PE SIGNAL ---
        pe_signal = False
        pe_reason = ""
        
        if macd < sig:
            jump = hist - p_hist
            if jump <= -MACD_JUMP_THRESHOLD:
                if rsi < p_rsi and rsi <= RSI_PE_MAX:
                    if adx >= ADX_MIN:
                        pe_signal = True
                
        if pe_signal:
            missed_trades.append({"Time": idx, "Type": "PE", "RSI": rsi, "MACD_Hist": hist, "Jump": hist - p_hist, "ADX": adx})

    if not missed_trades:
        print("RESULT: No signals matched all Hunter conditions today.")
    else:
        print(f"RESULT: Found {len(missed_trades)} potential trade signals.")
        for t in missed_trades:
            print(f"  [{t['Time'].strftime('%H:%M')}] Type: {t['Type']} | ADX: {t['ADX']:.1f} | RSI: {t['RSI']:.1f} | Jump: {t['Jump']:.2f}")

if __name__ == "__main__":
    run_audit("NIFTY", "scratch/missed_NIFTY.csv")
    run_audit("BANKNIFTY", "scratch/missed_BANKNIFTY.csv")
    run_audit("SENSEX", "scratch/missed_SENSEX.csv")
