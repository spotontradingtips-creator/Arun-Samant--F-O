import pandas as pd
from src.market_data import MStockAPI
from src.indicators import TechnicalIndicators
from src.trading_config import TradingConfig
from src.trading_models import TradeType
from src.fno_trading_bot import FnOTradingBot

def audit_entry_conditions():
    api = MStockAPI()
    config = TradingConfig()
    bot = FnOTradingBot(config)
    
    symbols = {
        'NIFTY': ('NSE', '26000', 'NIFTY'),
        'BANKNIFTY': ('NSE', '26009', 'NIFTY BANK'),
        'SENSEX': ('BSE', '51', 'SENSEX')
    }
    
    # We need vix for checks
    vix_quote = api.get_quote("INDIA VIX", "NSE")
    vix = vix_quote.get('last_price', 15.0) if vix_quote else 15.0
    
    print(f"--- ENTRY CONDITION AUDIT (VIX: {vix:.2f}) ---")
    
    for u, (ex, tok, sym) in symbols.items():
        # Using 15m as per strategy
        df, ok = api.get_hybrid_history(sym, ex, tok, '15minute')
        if df is None or df.empty:
            print(f"{u}: Failed to fetch data.")
            continue
            
        # Calculate indicators
        df['MACD'], df['MACD_Signal'], df['MACD_Hist'] = TechnicalIndicators.calculate_macd(df['close'])
        df['RSI'] = TechnicalIndicators.calculate_rsi(df['close'])
        adx, pdi, mdi = TechnicalIndicators.calculate_adx(df['high'], df['low'], df['close'])
        
        # Find Crossover Age
        def get_cross_age(m, s, tt):
            for j in range(len(m)-1, 0, -1):
                if tt == 'CE': # Bullish cross: prev m <= s, curr m > s
                    if m.iloc[j-1] <= s.iloc[j-1] and m.iloc[j] > s.iloc[j]:
                        return len(m) - 1 - j
                else: # Bearish cross: prev m >= s, curr m < s
                    if m.iloc[j-1] >= s.iloc[j-1] and m.iloc[j] < s.iloc[j]:
                        return len(m) - 1 - j
            return 999

        ce_age = get_cross_age(df['MACD'], df['MACD_Signal'], 'CE')
        pe_age = get_cross_age(df['MACD'], df['MACD_Signal'], 'PE')
        spot = df['close'].iloc[len(df)-1]
        last_time = df.index[len(df)-1]
        macd = df['MACD'].iloc[len(df)-1]
        sig = df['MACD_Signal'].iloc[len(df)-1]
        hist = df['MACD_Hist'].iloc[len(df)-1]
        rsi = df['RSI'].iloc[len(df)-1]
        curr_adx = adx.iloc[len(df)-1]
        curr_pdi = pdi.iloc[len(df)-1]
        curr_mdi = mdi.iloc[len(df)-1]
        
        print(f"\n{u} (@ {spot:.2f}) [Bar Time: {last_time}]:")
        print(f"  MACD: {macd:.2f} | Sig: {sig:.2f} | Hist: {hist:.2f} | CE Age: {ce_age} bars")
        print(f"  RSI: {rsi:.2f}")
        print(f"  ADX: {curr_adx:.2f} | +DI: {curr_pdi:.2f} | -DI: {curr_mdi:.2f}")
        
        idx = len(df) - 1
        # Check CE Conditions
        print(f"  [CHECK CALL (CE)]:")
        # Cond 1: MACD Crossover (Bullish) or Histogram Slope
        macd_bullish = macd > sig
        hist_slope = hist > df['MACD_Hist'].iloc[idx-1]
        print(f"    - MACD > Signal: {macd_bullish} ({macd:.2f} vs {sig:.2f})")
        print(f"    - Hist Slope Up: {hist_slope} ({hist:.2f} vs {df['MACD_Hist'].iloc[idx-1]:.2f})")
        
        # Cond 2: ADX Momentum
        adx_ok = curr_adx > 20
        di_ok = curr_pdi > curr_mdi
        print(f"    - ADX > 20: {adx_ok} ({curr_adx:.2f})")
        print(f"    - +DI > -DI: {di_ok} ({curr_pdi:.2f} vs {curr_mdi:.2f})")
        
        # Cond 3: RSI Bounds (USING CONFIG 70)
        rsi_ok = rsi < config.rsi_max
        print(f"    - RSI < {config.rsi_max}: {rsi_ok} ({rsi:.2f})")
        
        # Check PE Conditions
        print(f"  [CHECK PUT (PE)]:")
        macd_bearish = macd < sig
        hist_slope_down = hist < df['MACD_Hist'].iloc[idx-1]
        print(f"    - MACD < Signal: {macd_bearish} ({macd:.2f} vs {sig:.2f})")
        print(f"    - Hist Slope Down: {hist_slope_down} ({hist:.2f} vs {df['MACD_Hist'].iloc[idx-1]:.2f})")
        
        adx_p_ok = curr_adx > 20
        di_p_ok = curr_mdi > curr_pdi
        print(f"    - ADX > 20: {adx_p_ok} ({curr_adx:.2f})")
        print(f"    - -DI > +DI: {di_p_ok} ({curr_mdi:.2f} vs {curr_pdi:.2f})")
        
        rsi_p_ok = rsi > config.rsi_pe_min
        print(f"    - RSI > {config.rsi_pe_min}: {rsi_p_ok} ({rsi:.2f})")

if __name__ == "__main__":
    audit_entry_conditions()
