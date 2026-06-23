import yfinance as yf
import pandas as pd
import pandas_ta as ta
import numpy as np

def get_diagnostics(ticker, name):
    print(f"\n--- {name} ({ticker}) Diagnostics ---")
    
    # 1. Fetch Daily Data for ADX
    daily_data = yf.download(ticker, period="1y", interval="1d", progress=False)
    if isinstance(daily_data.columns, pd.MultiIndex): daily_data.columns = daily_data.columns.get_level_values(0)
    
    adx_df = daily_data.ta.adx(length=14)
    daily_adx = adx_df.iloc[-1, 0] if adx_df is not None else 0
    
    # 2. Fetch 15m Data for Strategy
    data_15m = yf.download(ticker, period="5d", interval="15m", progress=False)
    if isinstance(data_15m.columns, pd.MultiIndex): data_15m.columns = data_15m.columns.get_level_values(0)
    
    if data_15m.empty:
        print(f"No 15m data for {name}")
        return

    # RSI
    rsi_series = data_15m.ta.rsi(length=14)
    current_rsi = rsi_series.iloc[-1]
    prev_rsi = rsi_series.iloc[-2]
    rsi_flow = "RISING" if current_rsi > prev_rsi else "FALLING"

    # MACD
    macd_df = data_15m.ta.macd(fast=12, slow=26, signal=9)
    current_hist = macd_df.iloc[-1, 1]
    prev_hist = macd_df.iloc[-2, 1]
    macd_jump = current_hist - prev_hist

    # VWAP Proxy
    current_vwap = data_15m['Close'].rolling(window=20).mean().iloc[-1]
    current_price = data_15m['Close'].iloc[-1]
    
    # India VIX
    vix_data = yf.download("^INDIAVIX", period="1d", progress=False)
    if isinstance(vix_data.columns, pd.MultiIndex): vix_data.columns = vix_data.columns.get_level_values(0)
    vix = vix_data['Close'].iloc[-1] if not vix_data.empty else 0

    print(f"Price: {current_price:.2f} | VWAP(SMA20): {current_vwap:.2f}")
    print(f"Daily ADX: {daily_adx:.2f} (Target: > 22)")
    print(f"RSI: {current_rsi:.2f} (Target: 35-70, Flow: {rsi_flow})")
    print(f"MACD Jump: {macd_jump:.2f} (Target: > +1.5 for CE, < -1.5 for PE)")
    print(f"VIX: {vix:.2f} (Target: > 12)")

    # Condition Check Summary
    print("\n--- Summary ---")
    print(f"[Daily ADX] : {'PASS' if daily_adx > 22 else 'FAIL'}")
    print(f"[VIX]       : {'PASS' if vix > 12 else 'FAIL'}")
    print(f"[RSI Range] : {'PASS' if 35 <= current_rsi <= 70 else 'FAIL'}")
    
    # CE Check
    ce_jump_met = macd_jump >= 1.5
    ce_vwap_met = current_price > current_vwap
    ce_flow_met = rsi_flow == "RISING"
    ce_status = "READY" if (ce_jump_met and ce_vwap_met and ce_flow_met) else "WAITING"
    print(f"[CE (CALL)]  : {ce_status} (Jump:{ce_jump_met}, VWAP:{ce_vwap_met}, Flow:{ce_flow_met})")
    
    # PE Check
    pe_jump_met = macd_jump <= -1.5
    pe_vwap_met = current_price < current_vwap
    pe_flow_met = rsi_flow == "FALLING"
    pe_status = "READY" if (pe_jump_met and pe_vwap_met and pe_flow_met) else "WAITING"
    print(f"[PE (PUT)]   : {pe_status} (Jump:{pe_jump_met}, VWAP:{pe_vwap_met}, Flow:{pe_flow_met})")

indices = [
    ("^NSEI", "NIFTY"),
    ("^NSEBANK", "BANKNIFTY"),
    ("^BSESN", "SENSEX")
]

for ticker, name in indices:
    get_diagnostics(ticker, name)
