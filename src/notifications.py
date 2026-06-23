"""
Notification Module - Sends alerts to Telegram
"""

import os
import logging
import requests
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment
load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_ID = os.getenv("TELEGRAM_ADMIN_ID")

def send_telegram_alert(message: str):
    """Sends a message to the authorized admin on Telegram"""
    if not TOKEN or not ADMIN_ID:
        # Don't log error here to avoid spamming trading logs if not configured
        return False
        
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {
            "chat_id": ADMIN_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        resp = requests.post(url, json=payload, timeout=10)
        return resp.status_code == 200
    except Exception as e:
        logger.error(f"Failed to send Telegram alert: {e}")
        return False

def _normalize_name(name: str) -> str:
    """Helper to clean up index names for phone UI"""
    mapping = {
        "NIFTY 50": "NIFTY",
        "NIFTY50": "NIFTY",
        "NIFTY BANK": "BANKNIFTY",
        "NIFTYBANK": "BANKNIFTY",
        "SENSEX": "SENSEX"
    }
    return mapping.get(name.upper(), name)

def notify_trade_entry(underlying: str, trade_type: str, premium: float, spot: float, strike: float, trailing_sl: float = 0.0):
    """Standardized entry alert with clean Phone-First UI"""
    is_ce = "CE" in trade_type.upper() or "CALL" in trade_type.upper()
    emoji = "🟢" if is_ce else "🔴"
    trade_name = "CALL (CE)" if is_ce else "PUT (PE)"
    clean_underlying = _normalize_name(underlying)
    
    msg = (
        f"{emoji} **TRADE ENTERED: {trade_name}**\n\n"
        f"**Index**: {clean_underlying}\n"
        f"**Strike**: {int(strike) if strike else 'ATM'}\n"
        f"**Premium**: Rs {premium:,.2f}\n"
        f"**Spot Price**: {spot:,.2f}\n"
        f"━━━━━━━━━━━━━━━━\n"
    )
    
    if trailing_sl > 0:
        msg += f"🛡️ **Trailing SL Floor: Rs {trailing_sl:,.2f}**\n"
    else:
        msg += f"🛡️ **Safety Valve Active (-Rs 1,500)**\n"
        
    send_telegram_alert(msg)

def notify_trade_exit(underlying: str, exit_reason: str, pnl: float, daily_pnl: float, exit_premium: float, trailing_sl: float = 0.0):
    """Standardized exit alert with clean Phone-First UI"""
    status_emoji = "💰" if pnl > 0 else "🩸"
    profit_text = "PROFIT" if pnl > 0 else "LOSS"
    clean_underlying = _normalize_name(underlying)
    
    # Clean up internal exit reasons for the user
    clean_reason = exit_reason.replace("ExitReason.", "").replace("_", " ").title()
    if "Broker Sync" in clean_reason: clean_reason = "System Sync"
    if "1St-Trade" in clean_reason: clean_reason = "Safety Valve"

    msg = (
        f"{status_emoji} **TRADE CLOSED ({profit_text})**\n\n"
        f"**Index**: {clean_underlying}\n"
        f"**Reason**: {clean_reason}\n"
        f"**Exit Premium**: Rs {exit_premium:,.2f}\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"💵 **Trade P&L: Rs {pnl:+,.2f}**\n"
        f"🏦 **Total Daily P&L: Rs {daily_pnl:+,.2f}**\n"
    )
    
    if trailing_sl > 0:
        msg += f"🛡️ **Win-Lock Floor: Rs {trailing_sl:,.2f}**\n"
        
    if "Safety Valve" in clean_reason:
        msg += f"\n⏸️ **TRADING PAUSED**\n"
        msg += f"System has paused to protect your capital. Use the **RESUME** button in the Command Center to continue."

    msg += "\nKI is updated and up and running, I've made changes in the Manifest, and yes the floor is Synced"
    send_telegram_alert(msg)

def notify_floor_up(underlying: str, profit_crossed: float, new_floor: float):
    """Real-time ping when the trailing SL ladder climbs"""
    clean_underlying = _normalize_name(underlying)
    msg = (
        f"🚀 **FLOOR LOCKED!**\n\n"
        f"{clean_underlying} active profit just crossed **Rs {profit_crossed:,.2f}**.\n"
        f"**New Floor**: Rs {new_floor:,.2f}\n"
        f"You cannot lose on this trade."
    )
    send_telegram_alert(msg)

def notify_heartbeat(status: str, market_action: str, vix: float, trades_taken: int):
    """Periodic systemic status update"""
    from src.utils import now_ist
    current_time_str = now_ist().strftime('%I:%M %p')
    status_icon = "🟢" if "RUNNING" in status.upper() else "🔴"
    
    msg = (
        f"⏱️ **{current_time_str} HEARTBEAT**\n\n"
        f"**System Status**: {status_icon} {status}\n"
        f"**Market Action**: {market_action}\n"
        f"**VIX**: {vix:.2f}\n"
        f"**Trades Taken Today**: {trades_taken}\n\n"
        f"*actively scanning for indices. Standing by.*"
    )
    send_telegram_alert(msg)

def notify_eod_summary(date_str: str, month_str: str, 
                      daily_pnl: float, daily_trades: int, daily_winrate: float,
                      monthly_pnl: float, monthly_trades: int, monthly_winrate: float):
    """End of day comprehensive summary"""
    msg = (
        f"📊 **END OF DAY SUMMARY: {date_str}**\n\n"
        f"☀️ **TODAY'S PERFORMANCE**\n"
        f"**Daily P&L**: Rs {daily_pnl:+,.2f}\n"
        f"**Trades Taken**: {daily_trades}\n"
        f"**Daily Win Rate**: {daily_winrate:.1f}%\n\n"
        f"🗓️ **MONTHLY PERFORMANCE ({month_str.upper()})**\n"
        f"**Monthly P&L**: Rs {monthly_pnl:+,.2f}\n"
        f"**Total Trades in {month_str}**: {monthly_trades}\n"
        f"**Monthly Win Rate**: {monthly_winrate:.1f}%\n"
        f"━━━━━━━━━━━━━━━━\n"
        "KI is updated and up and running, I've made changes in the Manifest, and yes the floor is Synced"
    )
    send_telegram_alert(msg)

def notify_live_status(active_trade_pnl: float, daily_pnl: float, floor: float, peak: float):
    """High-frequency status heartbeat for active trades (Rule 47)"""
    distance_to_floor = daily_pnl - floor
    floor_emoji = "✅" if distance_to_floor > 250 else "⚠️"
    
    msg = (
        f"📊 **LIVE STATUS UPDATE**\n\n"
        f"💵 **Trade P&L**: Rs {active_trade_pnl:+,.2f}\n"
        f"🏦 **Today Realized**: Rs {daily_pnl:+,.2f}\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"🛡️ **Locked Floor**: Rs {floor:,.2f}\n"
        f"{floor_emoji} **Safety Buffer**: Rs {max(0, distance_to_floor):,.2f}\n"
        f"📈 **Today's High**: Rs {peak:,.2f}\n\n"
        f"*Sync: Heartbeat Active*"
    )
    send_telegram_alert(msg)

def notify_system_status(is_online: bool, reason: str = None):
    """Simple notification for system state changes"""
    emoji = "🟢" if is_online else "🔴"
    state = "ONLINE" if is_online else "OFFLINE"
    
    msg = f"{emoji} **SYSTEM {state}**\n\n"
    if reason:
        msg += f"**Reason**: {reason}\n"
    
    msg += f"━━━━━━━━━━━━━━━━\n"
    msg += "KI is updated and up and running, I've made changes in the Manifest, and yes the floor is Synced"
    send_telegram_alert(msg)
