"""
SENTINEL MOBILE CONTROL - Telegram Bot
Provides remote access to start/stop the bot and view P&L
"""

import os
import sys
import json
import logging
import asyncio
import psutil
import subprocess
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.persistence import StateManager
from src.otp_manager import OTPManager
from src.utils import now_ist

# Load environment
load_dotenv()

# Setup Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Constants
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_ID = os.getenv("TELEGRAM_ADMIN_ID")
BOT_SCRIPT = "main.py"

if not BOT_TOKEN or not ADMIN_ID:
    print("CRITICAL: TELEGRAM_BOT_TOKEN or TELEGRAM_ADMIN_ID missing in .env")
    sys.exit(1)

ADMIN_ID = int(ADMIN_ID)

# --- Helper Functions ---

def get_bot_process():
    """Find the running main.py process"""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmd = proc.info.get('cmdline') or []
            if any(BOT_SCRIPT in arg for arg in cmd):
                return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return None

def is_bot_running():
    return get_bot_process() is not None

def get_daily_pnl():
    """Calculate daily P&L from persistence state"""
    try:
        # Check active positions
        active_positions = StateManager.load_positions()
        active_pnl = 0.0
        # For active P&L we would technically need live quotes, 
        # but we can report the last known P&L from bot memory
        for pos in active_positions.values():
             if hasattr(pos, 'pnl') and pos.pnl:
                 active_pnl += pos.pnl

        # Load closed trades history
        history = StateManager.load_history()
        today = now_ist().date()
        closed_pnl = sum(p.pnl for p in history if p.entry_time.date() == today and p.pnl is not None)
        
        return active_pnl, closed_pnl, len(active_positions)
    except Exception as e:
        logger.error(f"Error calculating P&L: {e}")
        return 0.0, 0.0, 0

def get_control_keyboard():
    """Returns the persistent bottom keyboard"""
    keyboard = [
        ["🚀 START BOT", "🛑 STOP BOT"],
        ["📊 PERFORMANCE", "🔄 REFRESH"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# --- Command Handlers ---

async def restricted_access(update: Update):
    """Check if user is authorized"""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("ACCESS DENIED. You are not authorized to control this bot.")
        return False
    return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await restricted_access(update): return

    reply_markup = get_control_keyboard()
    
    status = "RUNNING" if is_bot_running() else "STOPPED"
    await update.message.reply_text(
        f"**SENTINEL COMMAND CENTER**\n\n"
        f"**SYSTEM STATUS**: {status}\n"
        f"**TIME**: {now_ist().strftime('%H:%M:%S')}\n"
        f"----------------------------\n"
        f"Use the persistent keyboard below to control the bot.",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        return

    if query.data == 'start_bot':
        keyboard = [[InlineKeyboardButton(" BACK TO MENU", callback_data='status_check')]]
        if is_bot_running():
            await query.edit_message_text(text="BOT IS ALREADY RUNNING.", reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await query.edit_message_text(text="INITIATING BOOT SEQUENCE...")
            # Start main.py as a background process
            subprocess.Popen([sys.executable, BOT_SCRIPT], 
                             creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)
            await asyncio.sleep(3) # Wait slightly longer for process to register
            await query.edit_message_text(text="BOT STARTED SUCCESSFULLY.", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == 'stop_bot':
        keyboard = [[InlineKeyboardButton(" BACK TO MENU", callback_data='status_check')]]
        if not is_bot_running():
            await query.edit_message_text(text="BOT IS NOT RUNNING.", reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            proc = get_bot_process()
            if proc:
                proc.terminate()
                await query.edit_message_text(text="SHUTTING DOWN...")
                await asyncio.sleep(1)
                await query.edit_message_text(text="BOT STOPPED.", reply_markup=InlineKeyboardMarkup(keyboard))
            else:
                await query.edit_message_text(text="FAILED TO STOP BOT.", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == 'pnl_check':
        active, closed, count = get_daily_pnl()
        total = active + closed
        
        msg = (
            f"**FINANCIAL DEBRIEF**\n\n"
            f"Active Pos: {count}\n"
            f"Closed P&L: Rs {closed:,.2f}\n"
            f"Active P&L: Rs {active:,.2f}\n"
            f"--------------------------------\n"
            f"**TOTAL P&L: Rs {total:,.2f}**\n"
        )
        # Add back buttons
        keyboard = [[InlineKeyboardButton("BACK", callback_data='status_check')]]
        await query.edit_message_text(text=msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

    elif query.data == 'status_check':
        status = "RUNNING" if is_bot_running() else "STOPPED"
        keyboard = [
            [InlineKeyboardButton("START BOT", callback_data='start_bot'),
             InlineKeyboardButton("STOP BOT", callback_data='stop_bot')],
            [InlineKeyboardButton("PERFORMANCE", callback_data='pnl_check'),
             InlineKeyboardButton("REFRESH", callback_data='status_check')]
        ]
        await query.edit_message_text(
            f"**SENTINEL COMMAND CENTER**\n\n"
            f"**SYSTEM STATUS**: {status}\n"
            f"**TIME**: {now_ist().strftime('%H:%M:%S')}\n",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

# --- OTP & Message Handlers ---

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles text messages (from persistent keyboard or manual entry)"""
    if not await restricted_access(update): return
    
    msg_text = update.message.text.strip()
    
    # 1. HANDLE PERSISTENT KEYBOARD COMMANDS
    if msg_text == "🚀 START BOT":
        if is_bot_running():
            await update.message.reply_text("BOT IS ALREADY RUNNING.")
        else:
            await update.message.reply_text("INITIATING BOOT SEQUENCE...")
            subprocess.Popen([sys.executable, BOT_SCRIPT], 
                             creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)
            await asyncio.sleep(3)
            await update.message.reply_text("BOT STARTED SUCCESSFULLY.")

    elif msg_text == "🛑 STOP BOT":
        if not is_bot_running():
            await update.message.reply_text("BOT IS NOT RUNNING.")
        else:
            proc = get_bot_process()
            if proc:
                proc.terminate()
                await update.message.reply_text("SHUTTING DOWN...")
                await asyncio.sleep(1)
                await update.message.reply_text("BOT STOPPED.")
            else:
                await update.message.reply_text("FAILED TO STOP BOT.")

    elif msg_text == "📊 PERFORMANCE":
        active, closed, count = get_daily_pnl()
        total = active + closed
        msg = (
            f"**FINANCIAL DEBRIEF**\n\n"
            f"Active Pos: {count}\n"
            f"Closed P&L: Rs {closed:,.2f}\n"
            f"Active P&L: Rs {active:,.2f}\n"
            f"--------------------------------\n"
            f"**TOTAL P&L: Rs {total:,.2f}**"
        )
        await update.message.reply_text(msg, parse_mode='Markdown')

    elif msg_text == "🔄 REFRESH":
        status = "RUNNING" if is_bot_running() else "STOPPED"
        await update.message.reply_text(
            f"**SENTINEL COMMAND CENTER**\n\n"
            f"**SYSTEM STATUS**: {status}\n"
            f"**TIME**: {now_ist().strftime('%H:%M:%S')}",
            parse_mode='Markdown'
        )

    # 2. HANDLE OTP ENTRY (6-digit)
    elif len(msg_text) == 6 and msg_text.isdigit():
        if OTPManager.check_for_pending_request():
            OTPManager.provide_otp(msg_text)
            await update.message.reply_text(f"OTP {msg_text} received and forwarded to trading bot.")
        else:
            await update.message.reply_text("No active OTP request found.")
    
    else:
        await update.message.reply_text("Use buttons below to control the bot or type /start to reset menu.")

async def check_otp_requests(bot):
    """Background task to notify user if an OTP is needed"""
    notified = False
    while True:
        if OTPManager.check_for_pending_request():
            if not notified:
                try:
                    await bot.send_message(
                        chat_id=ADMIN_ID,
                        text="**OTP REQUIRED**\n\nM-Stock login has expired. Please check your SMS and **type the 6-digit OTP here**.",
                        parse_mode='Markdown'
                    )
                    notified = True
                except Exception as e:
                    logger.error(f"Failed to send OTP notification: {e}")
        else:
            notified = False
        await asyncio.sleep(5)

# --- Entry Point ---

def main():
    print("Sentinel Mobile Control Starting...")
    print(f"Admin ID: {ADMIN_ID}")
    
    app = ApplicationBuilder().token(BOT_TOKEN).job_queue(None).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Telegram Listener Online. Awaiting Commands.")
    
    # Run the bot and the background task together
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Create the background task for OTP checking
    loop.create_task(check_otp_requests(app.bot))
    
    # Start polling
    app.run_polling()

if __name__ == '__main__':
    main()
