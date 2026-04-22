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
        # [MANDATORY 9:30 AM START] Rule 7: 9:15 AM + 15m Buffer
        market_start_dt = datetime.combine(now.date(), config.market_open).replace(tzinfo=now.tzinfo)
        effective_start_dt = market_start_dt + timedelta(minutes=config.morning_buffer_minutes)
        effective_start_time = effective_start_dt.time()
        
        if effective_start_time <= now_t <= config.market_close:
            logger.info(f"Market & Buffer Open ({effective_start_time}) - Commencing Turbo Ops.")
            return
            
        if now_t < effective_start_time:
            wait_secs = (effective_start_dt - now).total_seconds()
            logger.info(f"Waiting for 9:30 AM Start (Rules). Sleeping for {int(wait_secs)}s...")
            time.sleep(min(wait_secs, 60) if wait_secs > 0 else 1)
        else:
            logger.info("Market closed for today.")
            time.sleep(3600)

def get_market_data_with_indicators(api, symbol, exchange, token):
    try:
        quote = api.get_quote(symbol, exchange)
        spot = quote.get('last_price', 0) if quote else 0
        
        d_df = api.get_historical_data(symbol, exchange, token, "day", days=250)
        if d_df is None or len(d_df) < 250: 
            logger.warning(f"[STABILITY] {symbol}: Insufficient Daily History ({len(d_df)}/250 bars). Stabilization Guard active.")
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

        is_fresh = api.last_fetch_freshness.get(symbol, False)
        return d_df, i_df, spot, 15.0, stable, is_fresh
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
                    with bot.lock:
                        pos = bot.positions.get(u)
                        if not pos: continue
                    
                    spot = qs.get(u, {}).get('last_price', 0)
                    opt = qs.get(pos.option_symbol, {}).get('last_price', 0) if pos.option_symbol else 0
                    if spot <= 0 or opt <= 0: continue
                    
                    reason = None
                    if floor > 0 and (bot.daily_pnl + total_unrealized) <= floor:
                        reason = ExitReason.DAILY_WIN_LOCK
                    else:
                        reason = bot.check_exit_conditions(pos, opt, spot, 0, None)

                    if reason:
                        logger.warning(f"[TURBO EXIT] {u} ({reason})")
                        if config.live_trading:
                            order_managers_ex = "BFO" if "SENSEX" in u else "NFO"
                            order_manager.place_order(
                                api=api, 
                                symbol=pos.option_symbol, 
                                underlying=u, 
                                strike=pos.strike_price, 
                                option_type=pos.trade_type.value, # Corrected from p.option_type
                                qty=pos.lot_size, # Corrected from p.qty
                                side='SELL', 
                                exchange=order_managers_ex
                            )
                        bot.exit_trade(u, opt, spot, reason, api=api)
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
                except: pass

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
                        d, i, _, _, ok, fresh = get_market_data_with_indicators(api, broker_sym, exch, token)
                        if d is not None:
                            cache[u] = {'d': d, 'i': i, 't': time.time(), 'ok': ok, 'fresh': fresh}
                    else:
                        d, i, ok, fresh = state['d'], state['i'], state['ok'], state.get('fresh', True)
                        # [FIX] Set 'stable' and 'spot' if not in cache (standardizing variables)
                        stable = ok
                        
                        # [STABILITY GUARD] Validate spot against last bar
                        if not i.empty:
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
                                'low': min(last_close, spot), 'close': spot
                            }], index=[b_s])
                            i = pd.concat([i, new_bar])
                        else:
                            i.loc[b_s, 'close'] = spot
                            i.loc[b_s, 'high'] = max(i.loc[b_s, 'high'], spot)
                            i.loc[b_s, 'low'] = min(i.loc[b_s, 'low'], spot)
                            
                        # Complete indicator recalculation for accuracy (RSI/MACD strictly on 15m)
                        i['MACD'], i['MACD_Signal'], i['MACD_Hist'] = TechnicalIndicators.calculate_macd(i['close'])
                        i['RSI'] = TechnicalIndicators.calculate_rsi(i['close'])
                        i['ADX'], i['+DI'], i['-DI'] = TechnicalIndicators.calculate_adx(i['high'], i['low'], i['close'])
                        
                    if d is None or i is None: continue
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
                       quote = api.get_quote(broker_sym, exch)
                       if bot.check_exit_conditions(p, p.entry_price, spot, idx, i) == ExitReason.MACD_REVERSAL:
                           logger.info(f"[TURBO MACD EXIT] {name}")
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
                        tt = None
                        if bot.check_entry_conditions_ce(name, d, i, idx, vix, ok, spot, fresh): tt = TradeType.CE
                        elif bot.check_entry_conditions_pe(name, d, i, idx, vix, ok, spot, fresh): tt = TradeType.PE
                        
                        if tt:
                            strk, osym = OptionSelector.select_option(name, spot, tt.value, depth=config.strike_depth)
                            ex = "BFO" if "SENSEX" in name else "NFO"
                            pr = api.get_quote(osym, ex).get('last_price', 0) or (spot * 0.015)
                            
                            if config.live_trading:
                                norm_name = normalize_symbol(name)
                                qty = config.get_lot_size(norm_name)
                                r = order_manager.place_order(
                                    api=api, symbol=osym, underlying=name, strike=strk, 
                                    option_type=tt.value, qty=qty, side='BUY', 
                                    token=SymbolMaster().get_token(osym), exchange=ex
                                )
                                if r and r.status.value == 'PLACED': 
                                    bot.enter_trade(name, tt, pr, spot, vix, idx, option_symbol=osym, strike_price=strk)
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
