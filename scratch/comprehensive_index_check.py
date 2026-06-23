
import sys
import os
import pandas as pd
from datetime import datetime
import pytz
import logging

# Add src to path
sys.path.insert(0, os.getcwd())

from src.market_data import MStockAPI
from src.indicators import TechnicalIndicators
from src.trading_config import config
from src.utils import normalize_symbol

# Suppress logging for cleaner output
logging.getLogger("src.market_data").setLevel(logging.WARNING)
logging.getLogger("yfinance").setLevel(logging.CRITICAL)

def get_trend_status():
    api = MStockAPI()
    if not api.ensure_session_is_valid():
        print("Error: mStock Session invalid. Please run AUTHENTICATE.bat")
        return

    # Expanded Indices
    symbols_config = [
        {"name": "NIFTY", "exch": "NSE", "token": "26000", "broker_sym": "Nifty 50", "ticker": "^NSEI"},
        {"name": "BANKNIFTY", "exch": "NSE", "token": "26009", "broker_sym": "NIFTY BANK", "ticker": "^NSEBANK"},
        {"name": "SENSEX", "exch": "BSE", "token": "51", "broker_sym": "SENSEX", "ticker": "^BSESN"},
        {"name": "FINNIFTY", "exch": "NSE", "token": "26037", "broker_sym": "NIFTY FIN SERVICE", "ticker": "NIFTY_FIN_SERVICE.NS"},
        {"name": "MIDCPNIFTY", "exch": "NSE", "token": "26074", "broker_sym": "NIFTY MID SELECT", "ticker": "NIFTY_MID_SELECT.NS"}
    ]

    print(f"\n{'='*100}")
    print(f"COMPREHENSIVE INDEX TREND AUDIT | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*100}\n")

    results = []

    for item in symbols_config:
        name = item["name"]
        exch = item["exch"]
        token = item["token"]
        broker_sym = item["broker_sym"]
        ticker = item["ticker"]

        # 1. Get Quote
        quote = api.get_quote(broker_sym, exch)
        if not quote:
            # Try by token
            quote = api.get_quote(f"{exch}:{token}", exch)
        
        spot = quote.get('last_price', 0) if quote else 0
        if spot == 0:
            # Try YFinance for spot as last resort
            import yfinance as yf
            try:
                yt = yf.Ticker(ticker)
                hist = yt.history(period="1d", interval="1m")
                if not hist.empty:
                    spot = hist['Close'].iloc[-1]
            except:
                pass

        # 2. Daily ADX (Using YFinance for 250d stabilization & better alignment)
        daily_adx = 0
        try:
            import yfinance as yf
            df_yf = yf.download(ticker, period="2y", interval="1d", progress=False)
            if isinstance(df_yf.columns, pd.MultiIndex):
                df_yf.columns = [col[0] for col in df_yf.columns]
            df_yf = df_yf.rename(columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close'})
            
            # Inject today's live OHLC from broker into YF history for 100% accuracy
            quote = api.get_quote(name, exch)
            if quote and 'ohlc' in quote:
                q_ohlc = quote['ohlc']
                ist = pytz.timezone("Asia/Kolkata")
                today_ts = pd.Timestamp(datetime.now(ist).date())
                
                # Update or Append today's bar
                today_bar = pd.DataFrame([{
                    'open': q_ohlc['open'], 'high': q_ohlc['high'], 'low': q_ohlc['low'], 'close': quote['last_price']
                }], index=[today_ts])
                
                if today_ts in df_yf.index:
                    df_yf.update(today_bar)
                else:
                    df_yf = pd.concat([df_yf, today_bar])

            adx, _, _ = TechnicalIndicators.calculate_adx(df_yf['high'], df_yf['low'], df_yf['close'])
            daily_adx = adx.iloc[-1]
        except Exception as e:
            print(f"  [WARN] YFinance ADX Fallback failed for {name}: {e}")
            # Fallback to broker if YF fails
            d_df = api.get_historical_data(broker_sym, exch, token, "day", days=250)
            if d_df is not None and not d_df.empty:
                adx, _, _ = TechnicalIndicators.calculate_adx(d_df['high'], d_df['low'], d_df['close'])
                daily_adx = adx.iloc[-1]
        
        # 3. Intraday (15m)
        i_df, _ = api.get_hybrid_history(broker_sym, exch, token, "15minute", days=10)
        
        cur_rsi = 0
        cur_hist = 0
        prev_hist = 0
        rsi_rising = False
        rsi_falling = False
        hist_jump = 0

        if i_df is not None and not i_df.empty:
            # Inject current spot
            ist = pytz.timezone("Asia/Kolkata")
            now = datetime.now(ist)
            b_s = now.replace(minute=now.minute - now.minute % 15, second=0, microsecond=0)
            if b_s in i_df.index:
                i_df.loc[b_s, 'close'] = spot
            
            macd, signal, hist = TechnicalIndicators.calculate_macd(i_df['close'])
            rsi = TechnicalIndicators.calculate_rsi(i_df['close'])
            
            cur_rsi = rsi.iloc[-1]
            cur_hist = hist.iloc[-1]
            prev_hist = hist.iloc[-2]
            hist_jump = cur_hist - prev_hist
            
            rsi_rising = rsi.iloc[-1] > rsi.iloc[-2]
            rsi_falling = rsi.iloc[-1] < rsi.iloc[-2]

        # --- EVALUATE LEVELS ---
        # ADX Filters
        adx_standard = daily_adx > 20
        adx_hunter = daily_adx > 30
        
        # CE Checks
        ce_rsi_ok = cur_rsi <= 70.0
        ce_jump_ok = hist_jump >= 2.0
        
        ce_standard = adx_standard and ce_rsi_ok and rsi_rising and ce_jump_ok
        ce_hunter = adx_hunter and ce_rsi_ok and rsi_rising and ce_jump_ok

        # PE Checks
        pe_rsi_ok = cur_rsi <= 70.0
        pe_jump_ok = hist_jump <= -2.0
        
        pe_standard = adx_standard and pe_rsi_ok and rsi_falling and pe_jump_ok
        pe_hunter = adx_hunter and pe_rsi_ok and rsi_falling and pe_jump_ok

        print(f"--- {name} (Spot: {spot:.2f}) ---")
        print(f"  Indicators | ADX: {daily_adx:.2f} | RSI: {cur_rsi:.2f} (Rising: {rsi_rising}) | Jump: {hist_jump:+.2f}")
        
        print(f"  [CE STATUS]")
        print(f"    - Standard (ADX > 20): {'PASSED' if ce_standard else 'FAILED'}")
        print(f"    - Hunter   (ADX > 30): {'PASSED' if ce_hunter else 'FAILED'}")
        
        print(f"  [PE STATUS]")
        print(f"    - Standard (ADX > 20): {'PASSED' if pe_standard else 'FAILED'}")
        print(f"    - Hunter   (ADX > 30): {'PASSED' if pe_hunter else 'FAILED'}")
        print("-" * 60)

if __name__ == "__main__":
    check_now = get_trend_status()
