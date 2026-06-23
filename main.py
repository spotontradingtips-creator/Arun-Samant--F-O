"""
F&O Trading Bot - Main Entry Point
Optimized for TURBO EXECUTION (200ms / Parallel Fetching)
"""

import pandas as pd
import logging
import os
import sys
import time
import threading
import json
from datetime import datetime
import traceback

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

from src.fno_trading_bot import FnOTradingBot
from src.trading_models import TradeType, ExitReason, Position
from src.indicators import TechnicalIndicators
from src.trading_config import TradingConfig, config
from src.market_data import MStockAPI, IPMismatchError
from src.notifications import notify_system_status
from src.utils import setup_logging, now_ist, is_trading_day, console, print_holographic_banner
from src.option_selector import OptionSelector
from src.order_manager import OrderManager
from src.symbol_master import SymbolMaster
from src.position_sync import sync_positions_from_broker
from src.notifications import notify_heartbeat

# Futuristic styling
from rich.panel import Panel
from rich.live import Live
from rich.table import Table
from rich import box
from rich.layout import Layout

os.makedirs("logs", exist_ok=True)
log_file = f"logs/trading_bot_{datetime.now().strftime('%Y%m%d')}.log"
logger = setup_logging(log_file)

shutdown_event = threading.Event()

def wait_for_market_open():
    from datetime import datetime, timedelta
    while not shutdown_event.is_set():
        now = now_ist()
        if not is_trading_day(now):
            logger.info("MARKET CLOSED (Weekend/Holiday). System in SLEEP MODE.")
            time.sleep(3600); continue
            
        now_t = now.time()
        # [MANDATORY 10:00 AM START] Rule 76: 9:15 AM + 45m Buffer
        market_start_dt = datetime.combine(now.date(), config.market_open).replace(tzinfo=now.tzinfo)
        effective_start_dt = market_start_dt + timedelta(minutes=config.morning_buffer_minutes)
        effective_start_time = effective_start_dt.time()
        
        if effective_start_time <= now_t <= config.market_close:
            logger.info(f"Market & Buffer Open ({effective_start_time}) - Commencing Turbo Ops.")
            return
            
        if now_t < effective_start_time:
            wait_secs = (effective_start_dt - now).total_seconds()
            logger.info(f"Waiting for 10:00 AM Start (Rules). Sleeping for {int(wait_secs)}s...")
            time.sleep(min(wait_secs, 60) if wait_secs > 0 else 1)
        else:
            logger.info("Market closed for today.")
            time.sleep(3600)

def get_market_data_with_indicators(api, symbol, exchange, token, name):
    try:
        quote = api.get_quote(symbol, exchange)
        spot = quote.get('last_price', 0) if quote else 0
        
        # [RULE 97.1] Titan-Shield Primary: Bypass Broker Daily History for Indices, use Hybrid/YFinance
        if name in ["NIFTY", "BANKNIFTY", "SENSEX"]:
            d_df, _ = api.get_hybrid_history(symbol, exchange, token, "1day", days=250)
        else:
            d_df = api.get_historical_data(symbol, exchange, token, "1day", days=250)
            
        if d_df is None or len(d_df) < 250: 
            logger.warning(f"[STABILITY] {symbol}: Insufficient Daily History (Bars: {len(d_df) if d_df is not None else 0}/250). Stabilization Guard active.")
            return None, None, None, None, False, False
        
        d_df['MACD'], d_df['MACD_Signal'], d_df['MACD_Hist'] = TechnicalIndicators.calculate_macd(d_df['close'])
        d_df['RSI'] = TechnicalIndicators.calculate_rsi(d_df['close'])
        d_df['ADX'], d_df['+DI'], d_df['-DI'] = TechnicalIndicators.calculate_adx(d_df['high'], d_df['low'], d_df['close'])
        
        i_df, stable = api.get_hybrid_history(symbol, exchange, token, "15minute", days=10)
        
        if i_df is None or len(i_df) < 100: 
            if i_df is not None:
                logger.info(f"[WARM-UP] Indicators Warming Up for {symbol}: ({len(i_df)}/100 bars)...")
            return None, None, None, None, False, False
        
        ist = now_ist()
        b_s = ist.replace(minute=ist.minute - ist.minute % 15, second=0, microsecond=0)
        
        if b_s not in i_df.index:
            last_close = i_df.iloc[-1]['close']
            new_bar = pd.DataFrame([{
                'open': last_close, 'high': max(last_close, spot), 
                'low': min(last_close, spot), 'close': spot
            }], index=[b_s])
            i_df = pd.concat([i_df, new_bar])
        else:
            i_df.loc[b_s, 'close'] = spot
            i_df.loc[b_s, 'high'] = max(i_df.loc[b_s, 'high'], spot)
            i_df.loc[b_s, 'low'] = min(i_df.loc[b_s, 'low'], spot)

        i_df['MACD'], i_df['MACD_Signal'], i_df['MACD_Hist'] = TechnicalIndicators.calculate_macd(i_df['close'])
        i_df['RSI'] = TechnicalIndicators.calculate_rsi(i_df['close'])
        i_df['ADX'], i_df['+DI'], i_df['-DI'] = TechnicalIndicators.calculate_adx(i_df['high'], i_df['low'], i_df['close'])

        # [NEW] VWAP Implementation (Futures Volume Proxy)
        # 1. Fetch volume from front-month Future (Spot indices have 0 volume)
        f_info = SymbolMaster().future_tokens.get(name)
        if f_info:
            future_token = f_info['token']
            future_exch = f_info['exch']
            # Fetch last 2 days of 15m Futures history for volume
            f_df = api.get_historical_data(symbol, future_exch, future_token, "15minute", days=2)
            if f_df is not None and not f_df.empty:
                # Merge volume into i_df safely
                if 'volume' in f_df.columns:
                    try:
                        i_df = i_df.join(f_df[['volume']], rsuffix='_fut')
                        if 'volume_fut' in i_df.columns:
                            i_df['volume'] = i_df['volume_fut'].fillna(0)
                        else:
                            i_df['volume'] = i_df['volume'].fillna(0)
                    except Exception as e:
                        logger.error(f"[VWAP] {symbol}: Future Volume merge failed ({e}). VWAP disabled.")
                        i_df['VWAP'] = 0
                    # Calculate VWAP
                    i_df['VWAP'] = TechnicalIndicators.calculate_vwap(i_df)
                    logger.debug(f"[VWAP] {symbol}: Calculated using Future Proxy ({future_token})")
                else:
                    logger.warning(f"[VWAP] {symbol}: Future Proxy missing volume. VWAP disabled.")
                    i_df['VWAP'] = 0
            else:
                logger.warning(f"[VWAP] {symbol}: Could not fetch Future Volume for {future_token}. VWAP disabled.")
                i_df['VWAP'] = 0
        else:
            # For symbols with native volume (Stock Options/Futures)
            if 'volume' in i_df.columns:
                i_df['VWAP'] = TechnicalIndicators.calculate_vwap(i_df)
            else:
                i_df['VWAP'] = 0

        is_fresh = api.last_fetch_freshness.get(symbol, False)

        # Bug #13 Fix: Calculate actual historical volatility instead of hardcoded IV
        # Historical volatility = annualized standard deviation of daily returns
        try:
            import numpy as np
            daily_returns = np.log(d_df['close'] / d_df['close'].shift(1)).dropna()
            if len(daily_returns) > 1:
                # Annualize: std_dev * sqrt(252 trading days)
                historical_vol = daily_returns.std() * np.sqrt(252)
                iv = max(historical_vol * 100, 10.0)  # Convert to percentage, min 10% for safety
            else:
                iv = 15.0  # Fallback
        except Exception as vol_e:
            logger.debug(f"IV calculation error for {symbol}: {vol_e}, using fallback 15.0")
            iv = 15.0

        return d_df, i_df, spot, iv, stable, is_fresh
    except Exception as e:
        logger.error(f"Data Fetch Error ({symbol}): {e}")
        return None, None, None, None, False, False

def exit_monitoring_loop(api, bot, order_manager, symbols_config):
    logger.info("EXIT MONITORING THREAD STARTED (Turbo 200ms)")
    last_sync = time.time()
    
    while not shutdown_event.is_set():
        t0 = time.time()
        try:
            if now_ist().time() > config.market_close: break
            if time.time() - last_sync > 300:
                sync_positions_from_broker(bot, api)
                last_sync = time.time()

            with bot.lock:
                # Standardize current position keys to prevent Zombie Mode
                active_raw = list(bot.positions.keys())
                active = []
                for u in active_raw:
                    from src.utils import normalize_symbol
                    norm = normalize_symbol(u)
                    if norm != u:
                        logger.info(f"NORMALIZING ACTIVE POSITION KEY: {u} -> {norm}")
                        bot.positions[norm] = bot.positions.pop(u)
                    active.append(norm)
            
            if not active:
                time.sleep(1.0); continue

            # Parallel quote fetch (Spot + Options)
            f_list = []
            for u in active:
                with bot.lock:
                    pos = bot.positions.get(u)
                    if not pos: continue
                    f_list.append((u, symbols_config[u][0])) # (Symbol, Exchange)
                    if pos.option_symbol:
                        f_list.append((pos.option_symbol, "BFO" if "SENSEX" in u else "NFO"))

            qs = api.get_quotes_parallel(f_list)
            
            # Global P&L for Win-Lock
            total_unrealized = sum(p.calculate_pnl(qs.get(p.option_symbol,{}).get('last_price',0)) for p in bot.positions.values() if p.option_symbol)
            bot.update_daily_peak(bot.daily_pnl + total_unrealized)
            floor = bot.get_win_lock_floor()

            for u in active:
                try:
                    # Bug #2 Fix: Acquire lock for entire check-and-place-and-mutate sequence to prevent race conditions
                    with bot.lock:
                        pos = bot.positions.get(u)
                        if not pos:
                            continue

                        spot = qs.get(u, {}).get('last_price', 0)
                        opt = qs.get(pos.option_symbol, {}).get('last_price', 0) if pos.option_symbol else 0
                        if spot <= 0 or opt <= 0:
                            continue

                        pos.last_pnl = pos.calculate_pnl(opt)

                        reason = None
                        if floor > 0 and (bot.daily_pnl + total_unrealized) <= floor:
                            reason = ExitReason.DAILY_WIN_LOCK
                        else:
                            # Bug #2: check_exit_conditions reads/writes position state (max_pnl_reached, dynamic_trailing_sl)
                            # Must be called while holding lock to prevent torn reads/writes from concurrent entry thread
                            reason = bot.check_exit_conditions(pos, opt, spot, 0, None)

                    # Release lock before making API calls (place_order is I/O bound)
                    if reason:
                        logger.warning(f"[TURBO EXIT] {u} ({reason})")
                        # Bug #1 Fix: Only call exit_trade if order is PLACED, not REJECTED
                        order = None
                        if config.live_trading:
                            order_managers_ex = "BFO" if "SENSEX" in u else "NFO"
                            order = order_manager.place_order(
                                api=api,
                                symbol=pos.option_symbol,
                                underlying=u,
                                strike=pos.strike_price,
                                option_type=pos.trade_type.value, # Corrected from p.option_type
                                qty=pos.lot_size, # Corrected from p.qty
                                side='SELL',
                                exchange=order_managers_ex
                            )

                        # Only exit trade if order was successfully PLACED
                        if order is None or order.status.value == "PLACED":
                            with bot.lock:
                                bot.exit_trade(u, opt, spot, reason, api=api)
                        else:
                            logger.error(f"[ORDER REJECTED] Exit order for {u} was rejected. Position retained for retry. Reason: {order.rejection_reason}")
                            # Position remains in bot.positions for retry on next cycle
                except Exception as inner_e:
                    logger.error(f"Error monitoring {u}: {inner_e}")
                    continue

            dt = time.time() - t0
            time.sleep(max(0.01, 0.2 - dt))
        except Exception as e:
            logger.error(f"EXIT THREAD ERROR: {e}"); time.sleep(1)

def entry_monitoring_loop(api, bot, order_manager, symbols_config):
    from src.utils import normalize_symbol
    logger.info("ENTRY MONITORING THREAD STARTED (Turbo 200ms)")
    cache = {}
    last_hb = -1
    # Bug #3 Fix: Track pending orders per symbol to prevent duplicate entries
    order_pending = {}  # {symbol: True/False}
    
    while not shutdown_event.is_set():
        t0 = time.time()
        try:
            now = now_ist()
            if now.time() > config.market_close: break
            
            # Send Visual Heartbeat (Rule 9: 10:30, 12:30, 14:30)
            heartbeat_hours = {10, 12, 14}
            if now.hour in heartbeat_hours and now.minute == 30 and now.hour != last_hb:
                try:
                    vix_quote = api.get_quote("INDIA VIX", "NSE")
                    vix_val = vix_quote.get('last_price', 15.0) if vix_quote else 15.0
                    notify_heartbeat("RUNNING", "Turbo Monitoring Active (200ms).", vix_val, bot.daily_trades)
                    last_hb = now.hour
                except Exception as e:
                    # Bug #12 Fix: Log exceptions instead of silently swallowing them
                    logger.debug(f"Heartbeat notification error: {e}")

            # 1. Fetch data for all symbols
            s_list = [(v[2], v[0]) for v in symbols_config.values()]
            all_qs = api.get_quotes_parallel(s_list)
            vix_quote = api.get_quote("INDIA VIX", "NSE")
            vix = vix_quote.get('last_price', 15.0) if vix_quote else 15.0

            # [DATA_GUARD] Heartbeat Logging for Scavenger (Every 30s)
            static_timer = getattr(entry_monitoring_loop, "last_dg", 0)
            if time.time() - static_timer > 30:
                for u, (exch, token, broker_sym) in symbols_config.items():
                    spot = all_qs.get(broker_sym, {}).get('last_price', 0)
                    if spot > 0:
                        logger.info(f"[DATA_GUARD] {broker_sym} | PRICE: {spot:.2f} | TIME: {now.strftime('%H:%M:%S')}")
                    else:
                        logger.info(f"[DATA_GUARD] {broker_sym} | PRICE: 0.00 | TIME: {now.strftime('%H:%M:%S')} (BLIND)")
                entry_monitoring_loop.last_dg = time.time()

            for u, (exch, token, broker_sym) in symbols_config.items():
                try:
                    name = u # Internal Key (NIFTY, BANKNIFTY)
                    spot = all_qs.get(broker_sym, {}).get('last_price', 0)
                    
                    # [STABILITY GUARD] Reject invalid or extreme "Zero-Value" spikes
                    if spot <= 0: continue
                    
                    # Prevent wild spikes (e.g. from 24000 to 0 or 500000)
                    prev_close = 0 # To be fetched from cache below
                
                    # Check cache
                    state = cache.get(u)
                    if not state or (time.time() - state['t']) > 300:
                        d, i, _, _, ok, fresh = get_market_data_with_indicators(api, broker_sym, exch, token, u)
                        if d is not None:
                            cache[u] = {'d': d, 'i': i, 't': time.time(), 'ok': ok, 'fresh': fresh}
                    else:
                        d, i, ok, fresh = state['d'], state['i'], state['ok'], state.get('fresh', True)
                        # [FIX] Set 'stable' and 'spot' if not in cache (standardizing variables)
                        stable = ok
                        
                        # [STABILITY GUARD] Validate state
                        if i is None or i.empty or d is None or d.empty:
                            logger.warning(f"[RECOVERY] {u}: Indicators missing in cache. Forcing fresh fetch next cycle.")
                            if u in cache: del cache[u]
                            continue
                        else:
                            # [STABILITY GUARD] Validate spot against last bar
                            prev_c = i.iloc[-1]['close']
                            # If spot deviates by > 20% from last 15m closed price, it's likely bad data
                            if prev_c > 0 and abs(spot - prev_c) > (prev_c * 0.20):
                                logger.warning(f"[DATA GUARD] {u} rejected suspicious spot: {spot} (Prev 15m Close: {prev_c})")
                                continue
                            
                            b_s = now_ist().replace(minute=now_ist().minute - now_ist().minute % 15, second=0, microsecond=0)
                            if b_s not in i.index:
                                # Leading Edge Synthesis: Connect Friday's close to today's open
                                last_close = i.iloc[-1]['close']
                                new_bar = pd.DataFrame([{
                                    'open': last_close, 'high': max(last_close, spot), 
                                    'low': min(last_close, spot), 'close': spot, 'volume': 0
                                }], index=[b_s])
                                i = pd.concat([i, new_bar])
                            else:
                                i.loc[b_s, 'close'] = spot
                                i.loc[b_s, 'high'] = max(i.loc[b_s, 'high'], spot)
                                i.loc[b_s, 'low'] = min(i.loc[b_s, 'low'], spot)
                            
                    # Complete indicator recalculation for accuracy (RSI/MACD strictly on 15m)
                    if i is not None and not i.empty:
                        i['MACD'], i['MACD_Signal'], i['MACD_Hist'] = TechnicalIndicators.calculate_macd(i['close'])
                        i['RSI'] = TechnicalIndicators.calculate_rsi(i['close'])
                        i['ADX'], i['+DI'], i['-DI'] = TechnicalIndicators.calculate_adx(i['high'], i['low'], i['close'])
                        
                        # [NEW] Recalculate VWAP for leading edge
                        if 'volume' in i.columns:
                            # Attempt to update volume from live Future quote if available
                            f_info = SymbolMaster().future_tokens.get(name)
                            if f_info:
                                f_q = api.get_quote(f_info['token'], f_info['exch'])
                                if f_q and f_q.get('volume'):
                                    # Approximate 15m volume (since broker gives cumulative daily volume)
                                    # We'll use the cumulative volume for VWAP calculation
                                    i.loc[b_s, 'volume'] = f_q['volume']
                            
                            i['VWAP'] = TechnicalIndicators.calculate_vwap(i)
                        
                    # [LOGIC TRANSPARENCY] Heartbeat (Rule: Explicit visibility every 60s)
                    lg_timer = getattr(entry_monitoring_loop, "last_lg", {})
                    if time.time() - lg_timer.get(u, 0) > 60:
                        daily_adx = d.iloc[-1]['ADX'] if (d is not None and not d.empty and 'ADX' in d.columns) else 0
                        rsi_15m = i.iloc[-1]['RSI'] if (i is not None and not i.empty and 'RSI' in i.columns) else 0
                        vwap = i.iloc[-1].get('VWAP', 0) if (i is not None and not i.empty and 'VWAP' in i.columns) else 0
                        hist = i.iloc[-1].get('MACD_Hist', 0) if (i is not None and not i.empty and 'MACD_Hist' in i.columns) else 0
                        
                        status_msg = "OK" if (d is not None and i is not None and not i.empty) else "BLIND_DATA"
                        logger.info(f"[LOGIC_SNAPSHOT] {u:<10} | Status: {status_msg:<10} | Price: {spot:<8.2f} | VWAP: {vwap:<8.2f} | RSI: {rsi_15m:<5.2f} | ADX: {daily_adx:<5.2f} | Hist: {hist:<5.2f}")
                        lg_timer[u] = time.time()
                        entry_monitoring_loop.last_lg = lg_timer

                    # [SAFETY] Explicitly block processing if indicators failed to load
                    if d is None or i is None or i.empty: continue
                    idx = len(i) - 1
                    
                    # Reversal Check
                    if name in bot.positions:
                       underlying = name
                       if underlying in symbols_config:
                           exch, _, broker_sym = symbols_config[underlying]
                       else:
                           norm_u = normalize_symbol(underlying)
                           if norm_u in symbols_config:
                               exch, _, broker_sym = symbols_config[norm_u]
                           else: continue
                        
                       p = bot.positions[underlying]
                       
                       # Direct MACD reversal check (avoids false 0.00% P&L logging)
                       check_idx = idx - 1
                       macd_rev, di_rev = False, False
                       if check_idx > 0:
                           if p.trade_type == TradeType.CE:
                               macd_rev = TechnicalIndicators.check_macd_crossover_bearish(i['MACD'], i['MACD_Signal'], check_idx)
                               di_rev = TechnicalIndicators.check_di_crossover_bearish(i['+DI'], i['-DI'], check_idx)
                           else:
                               macd_rev = TechnicalIndicators.check_macd_crossover_bullish(i['MACD'], i['MACD_Signal'], check_idx)
                               di_rev = TechnicalIndicators.check_di_crossover_bullish(i['+DI'], i['-DI'], check_idx)
                               
                       if macd_rev or di_rev:
                           logger.info(f"[TURBO MACD EXIT] {name} - Trend Reversal CONFIRMED")
                           ex = "BFO" if "SENSEX" in name else "NFO"
                           pr = api.get_quote(p.option_symbol, ex).get('last_price', 0)
                           if config.live_trading: 
                               order_manager.place_order(
                                   api=api, 
                                   symbol=p.option_symbol, 
                                   underlying=name, 
                                   strike=p.strike_price, 
                                   option_type=p.trade_type.value, 
                                   qty=p.lot_size, 
                                   side='SELL', 
                                   exchange=ex
                               )
                           bot.exit_trade(name, pr, spot, ExitReason.MACD_REVERSAL, api=api)
                    
                    # Entry Check
                    elif name not in bot.positions:
                        # Bug #3 Fix: Check if order is already pending for this symbol
                        if order_pending.get(name, False):
                            logger.debug(f"[DUPLICATE_GUARD] Entry order still pending for {name}. Skipping to prevent duplicate.")
                            continue  # Skip if order already pending

                        # Bug #5 Fix: Check daily loss limit before entering new position
                        max_daily_loss = -(config.initial_capital * config.daily_loss_limit_percent / 100)
                        if bot.daily_pnl <= max_daily_loss:
                            logger.warning(f"[CIRCUIT BREAKER] Daily loss limit exceeded. Daily P&L: {bot.daily_pnl:.2f} vs Limit: {max_daily_loss:.2f}. No new entries allowed.")
                            continue  # Skip entry for this symbol

                        tt = None
                        if bot.check_entry_conditions_ce(name, d, i, idx, vix, ok, spot, fresh): tt = TradeType.CE
                        elif bot.check_entry_conditions_pe(name, d, i, idx, vix, ok, spot, fresh): tt = TradeType.PE

                        if tt:
                            strk, osym = OptionSelector.select_option(name, spot, tt.value, depth=config.strike_depth)
                            ex = "BFO" if "SENSEX" in name else "NFO"
                            pr = api.get_quote(osym, ex).get('last_price', 0) or (spot * 0.015)

                            if config.live_trading:
                                # Bug #3: Set order_pending flag BEFORE placing order to block concurrent attempts
                                order_pending[name] = True
                                try:
                                    norm_name = normalize_symbol(name)
                                    qty = config.get_lot_size(norm_name)
                                    r = order_manager.place_order(
                                        api=api, symbol=osym, underlying=name, strike=strk,
                                        option_type=tt.value, qty=qty, side='BUY',
                                        token=SymbolMaster().get_token(osym), exchange=ex
                                    )
                                    if r and r.status.value == 'PLACED':
                                        bot.enter_trade(name, tt, pr, spot, vix, idx, option_symbol=osym, strike_price=strk)
                                    # Clear flag after order completes (success or failure)
                                    order_pending[name] = False
                                except Exception as e:
                                    logger.error(f"Error placing entry order for {name}: {e}")
                                    # Clear flag even on error to allow retry next cycle
                                    order_pending[name] = False
                            else:
                                bot.enter_trade(name, tt, pr, spot, vix, idx, option_symbol=osym, strike_price=strk)
                except Exception as inner_e:
                    logger.error(f"Error processing {u} in entry loop: {inner_e}")
                    continue

            dt = time.time() - t0
            time.sleep(max(0.01, 0.2 - dt))
        except Exception as e:
            logger.error(f"ENTRY THREAD ERROR: {e}"); time.sleep(1)

def background_sync_loop(api, bot):
    """
    Independent thread for:
    1. 'Ground Truth' realized P&L sync from broker (Every 5 mins)
    2. 'Live Status' Telegram heartbeats (Every 60 secs when trade active)
    """
    logger.info("BACKGROUND SYNC & STATUS THREAD STARTED")
    last_heavy_sync = 0
    
    while not shutdown_event.is_set():
        current_time = time.time()
        
        try:
            # 1. HEAVY SYNC (Every 5 minutes)
            if current_time - last_heavy_sync >= 300:
                bot.sync_daily_pnl(api)
                last_heavy_sync = current_time
            
            # 2. LIVE STATUS HEARTBEAT (Every 60 seconds if active trade)
            if bot.positions:
                active_pnl = 0.0
                for pos in bot.positions.values():
                    # We use the internal monitor price if available
                    active_pnl += getattr(pos, 'last_pnl', 0.0)
                
                from src.notifications import notify_live_status
                notify_live_status(
                    active_trade_pnl=active_pnl,
                    daily_pnl=bot.daily_pnl,
                    floor=bot.get_win_lock_floor(),
                    peak=bot.daily_max_pnl
                )
        except Exception as e:
            logger.error(f"BACKGROUND SYNC ERROR: {e}")
        
        # Interval check (60 seconds)
        for _ in range(60):
            if shutdown_event.is_set(): break
            time.sleep(1)

def run_live_trading():
    """Main execution loop for the trading bot"""
    from src.notifications import notify_system_status
    try:
        api = MStockAPI(); 
        if not api.ensure_session_is_valid(): return
        
        # [NEW] PRE-FLIGHT SYSTEM CHECK (Rule-Aligned)
        if not api.validate_connection():
            logger.critical("Pre-Flight Check Failed. Aborting startup for safety.")
            notify_system_status(False, "Startup Failed: Pre-Flight Check (Indices Offline)")
            return
        
        # Send ONLINE notification immediately upon successful connection
        notify_system_status(is_online=True)
        
        bot = FnOTradingBot(config, api=api); order_manager = OrderManager(config)
        
        # [MANDATORY] Capital Sync (Rule 15)
        try:
            live_funds = api.get_funds()
            if live_funds and live_funds > 0:
                bot.sync_starting_capital(live_funds)
            else:
                logger.warning("Could not sync live funds. Using config default.")
        except Exception as e:
            logger.error(f"Capital Sync Error: {e}")
        
        # Structure: {InternalKey: (Exchange, Token, BrokerSymbol)}
        symbols_config = {
            "NIFTY": ("NSE", "26000", "NIFTY"),
            "BANKNIFTY": ("NSE", "26009", "NIFTY BANK"), # Hardcoded to token 26009 for stability
            "SENSEX": ("BSE", "51", "SENSEX")
        }
        
        wait_for_market_open()
        sync_positions_from_broker(bot, api)
        
        ex_t = threading.Thread(target=exit_monitoring_loop, args=(api, bot, order_manager, symbols_config), name="ExitT", daemon=True)
        en_t = threading.Thread(target=entry_monitoring_loop, args=(api, bot, order_manager, symbols_config), name="EntryT", daemon=True)
        bg_t = threading.Thread(target=background_sync_loop, args=(api, bot), name="SyncT", daemon=True)
        
        ex_t.start(); en_t.start(); bg_t.start()
        
        while not shutdown_event.is_set():
            if now_ist().time() > config.market_close: 
                shutdown_event.set()
                break
            
            # [ANTI-ZOMBIE] Master Watchdog for Background Threads
            # Ensuring no core monitoring logic has crashed silently
            dead_threads = []
            if not ex_t.is_alive(): dead_threads.append("Exit-Monitor")
            if not en_t.is_alive(): dead_threads.append("Entry-Scanner")
            if not bg_t.is_alive(): dead_threads.append("Sync-Heartbeat")
            
            if dead_threads:
                reason = f"CRITICAL: Zombie State Detected! Dead threads: {', '.join(dead_threads)}"
                logger.critical(reason)
                notify_system_status(is_online=False, reason=reason)
                shutdown_event.set() # Safe termination of remaining threads
                break
                
            time.sleep(10)
    except IPMismatchError as e:
        logger.critical(f"[FATAL] {e}")
        import requests
        try:
            curr_ip = requests.get("https://api.ipify.org", timeout=5).text
        except:
            curr_ip = "Unknown"
        
        reason = f"IP Mismatch! Update mStock Portal with: {curr_ip}"
        notify_system_status(is_online=False, reason=reason)
        # We don't use sys.exit(1) inside a function that might be called elsewhere,
        # but in run_live_trading it's mostly fine. 
        # Actually, let's just re-raise or handle it in __main__.
        raise e
    except KeyboardInterrupt: shutdown_event.set()
    finally:
        shutdown_event.set()
        # Ensure threads have time to clean up if joined

if __name__ == "__main__":
    try:
        run_live_trading()
    except Exception as e:
        error_msg = str(e)
        logger.error(f"FATAL SYSTEM ERROR: {error_msg}")
        # Only notify if it's not a keyboard interrupt shutdown
        if not isinstance(e, KeyboardInterrupt):
            from src.notifications import notify_system_status
            notify_system_status(is_online=False, reason=f"Fatal System Error: {error_msg}")
        sys.exit(1)
