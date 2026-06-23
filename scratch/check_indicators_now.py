
import sys
import os
import pandas as pd
from datetime import datetime
import pytz

# Add src to path
sys.path.insert(0, os.getcwd())

from src.market_data import MStockAPI
from src.indicators import TechnicalIndicators
from src.trading_config import config

def check_now():
    api = MStockAPI()
    if not api.ensure_session_is_valid():
        print("Session invalid")
        return

    symbols_config = {
        "NIFTY": ("NSE", "26000", "NIFTY"),
        "BANKNIFTY": ("NSE", "26009", "NIFTY BANK"),
        "SENSEX": ("BSE", "51", "SENSEX")
    }

    print(f"\n--- Strategy Status: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
    
    vix_quote = api.get_quote("INDIA VIX", "NSE")
    vix = vix_quote.get('last_price', 15.0) if vix_quote else 15.0
    print(f"INDIA VIX: {vix:.2f}")

    for name, (exch, token, broker_sym) in symbols_config.items():
        print(f"\n--- {name} ---")
        quote = api.get_quote(broker_sym, exch)
        spot = quote.get('last_price', 0) if quote else 0
        print(f"Spot: {spot}")
        
        # Daily ADX
        d_df = api.get_historical_data(broker_sym, exch, token, "day", days=60)
        if d_df is not None and not d_df.empty:
            adx, plus_di, minus_di = TechnicalIndicators.calculate_adx(d_df['high'], d_df['low'], d_df['close'])
            daily_adx = adx.iloc[-1]
            print(f"Daily ADX: {daily_adx:.2f} (Min: 30.0) -> {'OK' if daily_adx > 30 else 'NOT MET'}")
        else:
            print("Daily data fetch failed")

        # Intraday MACD & RSI (15m)
        i_df, stable = api.get_hybrid_history(broker_sym, exch, token, "15minute", days=10)
        if i_df is not None and not i_df.empty:
            # Update last bar with current spot
            ist = pytz.timezone("Asia/Kolkata")
            now = datetime.now(ist)
            b_s = now.replace(minute=now.minute - now.minute % 15, second=0, microsecond=0)
            if b_s in i_df.index:
                i_df.loc[b_s, 'close'] = spot
            
            macd, signal, hist = TechnicalIndicators.calculate_macd(i_df['close'])
            rsi = TechnicalIndicators.calculate_rsi(i_df['close'])
            
            cur_macd = macd.iloc[-1]
            cur_sig = signal.iloc[-1]
            cur_hist = hist.iloc[-1]
            cur_rsi = rsi.iloc[-1]
            prev_hist = hist.iloc[-2]
            
            print(f"15m RSI: {cur_rsi:.2f} (Range: 30-70) -> {'OK' if 30 <= cur_rsi <= 70 else 'NOT MET'}")
            print(f"15m MACD: {cur_macd:.2f}, Signal: {cur_sig:.2f}")
            print(f"15m Histogram: {cur_hist:.2f} (Prev: {prev_hist:.2f})")
            
            # CE Conditions
            ce_trend = cur_macd > cur_sig
            ce_momentum = cur_hist > (prev_hist + 2.0)
            print(f"CE Trend (MACD > Sig): {ce_trend}")
            print(f"CE Momentum Jump (+2.0): {ce_momentum}")
            
            # PE Conditions
            pe_trend = cur_macd < cur_sig
            pe_momentum = cur_hist < (prev_hist - 2.0)
            print(f"PE Trend (MACD < Sig): {pe_trend}")
            print(f"PE Momentum Jump (-2.0): {pe_momentum}")
            
        else:
            print("Intraday data fetch failed")

if __name__ == "__main__":
    check_now()
