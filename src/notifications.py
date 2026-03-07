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

def notify_trade_entry(underlying: str, trade_type: str, premium: float, spot: float, strike: float):
    """Standardized entry alert"""
    msg = (
        f"**TRADE ENTERED**\n\n"
        f"**Underlying**: {underlying}\n"
        f"**Option**: {trade_type}\n"
        f"**Strike**: {strike}\n"
        f"**Premium**: Rs {premium:,.2f}\n"
        f"**Spot**: {spot:,.2f}\n"
    )
    send_telegram_alert(msg)

def notify_trade_exit(underlying: str, exit_reason: str, pnl: float, daily_pnl: float, exit_premium: float):
    """Standardized exit alert"""
    msg = (
        f"**TRADE CLOSED**\n\n"
        f"**Underlying**: {underlying}\n"
        f"**Reason**: {exit_reason}\n"
        f"**Exit Premium**: Rs {exit_premium:,.2f}\n"
        f"------------------------------\n"
        f"**Trade P&L: Rs {pnl:,.2f}**\n"
        f"**Daily P&L: Rs {daily_pnl:,.2f}**\n"
    )
    send_telegram_alert(msg)
