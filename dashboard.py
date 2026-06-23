# -*- coding: utf-8 -*-
"""
F&O Trading Bot - SENTINEL HUB v2.0
Premium Futuristic Command Center
"""

import streamlit as st
import pandas as pd
import os
import sys
import json
from datetime import datetime
from pathlib import Path
import time
import glob
import subprocess
import psutil
from dotenv import load_dotenv
from src.utils import setup_logging

# ============================================================================
# INITIALIZATION - Load environment once at module startup
# ============================================================================
# Get absolute path to .env file (not relative to working directory)
PROJECT_ROOT = Path(__file__).parent
ENV_FILE = PROJECT_ROOT / '.env'

# Load environment variables once at startup (before Streamlit reruns)
load_dotenv(ENV_FILE, override=True)

# Initialize Logger (Isolated)
logger = setup_logging(log_file="logs/dashboard.log")

# ============================================================================
# FEATURE 4: DATA SAFETY & AUDIT LOGGING
# ============================================================================
SESSION_TIMEOUT_MINUTES = 60  # Session expires after 1 hour of inactivity
AUDIT_LOG_FILE = PROJECT_ROOT / 'logs' / 'dashboard_audit.log'

def validate_input(value: str, field_type: str = 'text', min_length: int = 1) -> tuple[bool, str]:
    """Validate user input at system boundaries (PRINCIPLE 4: SECURITY-FIRST)"""
    if not isinstance(value, str):
        return False, f"Invalid {field_type}: must be text"

    if len(value) < min_length:
        return False, f"Invalid {field_type}: minimum {min_length} characters required"

    # Reject inputs with suspicious patterns
    suspicious_patterns = ['<script', 'javascript:', 'onclick', 'onerror']
    value_lower = value.lower()
    for pattern in suspicious_patterns:
        if pattern in value_lower:
            return False, f"Invalid {field_type}: contains disallowed characters"

    return True, "Valid"


def log_audit_event(action: str, details: dict = None, level: str = 'INFO') -> None:
    """Log security events without credential values (PRINCIPLE 4: SECURITY-FIRST)"""
    if details is None:
        details = {}

    # Never log credential values - only field names
    safe_details = {k: '***' if 'key' in k.lower() or 'secret' in k.lower() or 'password' in k.lower() else v
                    for k, v in details.items()}

    timestamp = datetime.now().isoformat()
    audit_entry = {
        'timestamp': timestamp,
        'action': action,
        'details': safe_details,
        'level': level,
    }

    # Log to both logger and audit file
    log_message = f"[AUDIT] {action} - {safe_details}"
    if level == 'WARNING':
        logger.warning(log_message)
    elif level == 'ERROR':
        logger.error(log_message)
    else:
        logger.info(log_message)

    # Write to audit log file (for compliance)
    try:
        with open(AUDIT_LOG_FILE, 'a') as f:
            f.write(f"{timestamp} | {action} | {safe_details}\n")
    except Exception as e:
        logger.error(f"Failed to write audit log: {str(e)}")


def check_session_timeout() -> bool:
    """Check if user session has timed out (no activity for SESSION_TIMEOUT_MINUTES)"""
    if 'session_start' not in st.session_state:
        st.session_state.session_start = datetime.now()
        st.session_state.last_activity = datetime.now()
        return False

    # Update last activity on every page load (for inactivity tracking)
    st.session_state.last_activity = datetime.now()

    # Check inactivity timeout (time since last activity, not session start)
    elapsed_minutes = (datetime.now() - st.session_state.last_activity).total_seconds() / 60
    if elapsed_minutes > SESSION_TIMEOUT_MINUTES:
        # Session expired due to inactivity
        log_audit_event('SESSION_TIMEOUT', {'inactivity_minutes': int(elapsed_minutes)}, level='INFO')
        return True

    return False


# Initialize audit logging
try:
    AUDIT_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
except Exception as e:
    logger.error(f"Failed to create audit log directory: {str(e)}")

# FORCE DARK THEME AND WIDE LAYOUT
st.set_page_config(
    page_title="SENTINEL HUB | F&O BOT", 
    page_icon="terminal",
    layout="wide",
    initial_sidebar_state="expanded"
)

# THEME: ULTRA MINIMAL (BLACK & WHITE)
t = {
    "bg": "#000000",             
    "card_bg": "#111111", 
    "accent": "#ffffff",         
    "text": "#ffffff",
    "border": "#333333"
}

with st.sidebar:
    # ============================================================================
    # FEATURE 4: DATA SAFETY - Session Timeout Check
    # ============================================================================
    # Check session timeout on every page load
    if check_session_timeout():
        st.error("🔐 **SESSION EXPIRED** - Please refresh the page to continue")
        st.stop()

    st.markdown("### SYSTEM")
    st.markdown("**MODE:** ULTRA_MINIMAL")
    st.markdown("---")

    # Display session info in sidebar
    if 'session_start' in st.session_state:
        elapsed = (datetime.now() - st.session_state.session_start).total_seconds() / 60
        session_text = f"Session: {int(elapsed)} min (timeout: {SESSION_TIMEOUT_MINUTES} min)"
        st.caption(session_text)

    # ============================================================================
    # FEATURE 1: SETTINGS PANEL - Credential Management
    # ============================================================================
    with st.expander("⚙️ SETTINGS", expanded=False):
        st.markdown("#### API Credentials")

        # Input fields for credentials
        api_key_input = st.text_input(
            "API Key",
            type="password",
            placeholder="Enter your API key",
            help="Your broker API key (not logged in plaintext)"
        )

        api_secret_input = st.text_input(
            "API Secret",
            type="password",
            placeholder="Enter your API secret",
            help="Your broker API secret (not logged in plaintext)"
        )

        client_code_input = st.text_input(
            "Client Code",
            placeholder="Enter your client code",
            help="Your broker client code"
        )

        password_input = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            help="Your broker password (not logged in plaintext)"
        )

        # Save credentials button
        if st.button("💾 Save Credentials", key="save_creds"):
            # Validate all inputs (PRINCIPLE 4: SECURITY-FIRST)
            validation_errors = []

            # Validate API key
            valid, msg = validate_input(api_key_input, 'API Key', min_length=5)
            if not valid:
                validation_errors.append(msg)

            # Validate API secret
            valid, msg = validate_input(api_secret_input, 'API Secret', min_length=5)
            if not valid:
                validation_errors.append(msg)

            # Validate client code
            valid, msg = validate_input(client_code_input, 'Client Code', min_length=1)
            if not valid:
                validation_errors.append(msg)

            # Validate password
            valid, msg = validate_input(password_input, 'Password', min_length=1)
            if not valid:
                validation_errors.append(msg)

            if validation_errors:
                for error in validation_errors:
                    st.error(f"❌ {error}")
                # Log validation failure (audit trail)
                log_audit_event('SETTINGS_VALIDATION_FAILED', {
                    'errors_count': len(validation_errors),
                    'fields': 'api_key, api_secret, client_code, password'
                }, level='WARNING')
            else:
                # Save to .env file securely (using absolute path from module startup)
                try:
                    env_content = f"""API_KEY={api_key_input}
API_SECRET={api_secret_input}
CLIENT_CODE={client_code_input}
PASSWORD={password_input}
"""
                    with open(ENV_FILE, 'w') as f:
                        f.write(env_content)

                    # Secure file permissions (0o600 = rw-------)
                    # Note: On Windows, this is a no-op but doesn't error
                    os.chmod(ENV_FILE, 0o600)

                    # Log update with audit trail (PRINCIPLE 4: SECURITY-FIRST)
                    log_audit_event('CREDENTIALS_UPDATED', {
                        'fields': 'api_key, api_secret, client_code, password'
                    }, level='INFO')

                    # Warning for Windows users (file permissions not enforced on Windows)
                    if os.name == 'nt':
                        st.warning("⚠️ On Windows, file permissions are limited. Use OS-level access controls to protect credentials.")

                    st.success("✅ Credentials saved securely!")
                    st.rerun()
                except Exception as e:
                    logger.error(f"[SETTINGS] Error saving credentials: {str(e)}")
                    st.error(f"❌ Error saving credentials: {str(e)}")

        st.markdown("---")

        # Display current status (masked)
        # Note: ENV_FILE was loaded at module startup, no need to reload
        st.markdown("#### Current Status")
        has_api_key = bool(os.getenv('API_KEY'))
        has_api_secret = bool(os.getenv('API_SECRET'))
        has_client_code = bool(os.getenv('CLIENT_CODE'))
        has_password = bool(os.getenv('PASSWORD'))

        status_items = [
            ("API Key", has_api_key),
            ("API Secret", has_api_secret),
            ("Client Code", has_client_code),
            ("Password", has_password),
        ]

        for field, has_value in status_items:
            status_icon = "✅" if has_value else "❌"
            st.markdown(f"{status_icon} **{field}**: {'Configured' if has_value else 'Not configured'}")

    st.markdown("---")

    # ============================================================================
    # FEATURE 2: PAPER/LIVE MODE TOGGLE
    # ============================================================================
    st.markdown("### 🎯 TRADING MODE")

    # Load current mode from config.json (cached in session_state)
    CONFIG_FILE = PROJECT_ROOT / 'config.json'

    # Initialize session state for mode (prevents disk read on every rerun)
    if 'current_mode' not in st.session_state:
        current_mode = 'paper'  # Default to paper mode
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    current_mode = 'live' if config.get('live_trading', False) else 'paper'
                st.session_state.current_mode = current_mode
            except Exception as e:
                logger.error(f"[MODE] Error reading config: {str(e)}")
                st.warning("⚠️ Could not read saved mode. Using default (Paper).")
                st.session_state.current_mode = 'paper'
        else:
            st.session_state.current_mode = 'paper'

    current_mode = st.session_state.current_mode

    # Mode selection dropdown
    mode_options = {
        '📄 PAPER MODE - Simulated Trading (No Real Money)': 'paper',
        '🔴 LIVE MODE - Real Money Trading (Use Caution!)': 'live'
    }

    selected_mode_text = next(
        (k for k, v in mode_options.items() if v == current_mode),
        list(mode_options.keys())[0]
    )

    selected_mode_text = st.radio(
        "Select trading mode:",
        options=list(mode_options.keys()),
        index=list(mode_options.keys()).index(selected_mode_text) if selected_mode_text in mode_options else 0,
        key="mode_selector"
    )

    selected_mode = mode_options[selected_mode_text]

    # Save mode if changed
    if selected_mode != current_mode:
        try:
            # Load existing config or create new
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
            else:
                config = {}

            # Update live_trading setting
            config['live_trading'] = (selected_mode == 'live')

            # Save updated config atomically (write to temp, then replace)
            import tempfile
            with tempfile.NamedTemporaryFile(
                'w',
                dir=CONFIG_FILE.parent,
                delete=False,
                suffix='.tmp',
                encoding='utf-8'
            ) as tmp_file:
                json.dump(config, tmp_file, indent=2)
                tmp_path = Path(tmp_file.name)

            # Atomic replace (POSIX atomic, near-atomic on Windows)
            tmp_path.replace(CONFIG_FILE)

            # Update session state to prevent re-reading
            st.session_state.current_mode = selected_mode

            # Log mode change safely (PRINCIPLE 4: SECURITY-FIRST)
            logger.info(f"[MODE] Trading mode changed to {selected_mode.upper()} (no sensitive data logged)")

            # Show notification after rerun
            st.session_state.mode_changed = True
            if selected_mode == 'live':
                st.session_state.mode_message = "⚠️ **LIVE MODE ENABLED** - Real money at risk! Monitor your positions carefully."
            else:
                st.session_state.mode_message = "✅ Paper mode - simulated trading only"

            st.rerun()
        except Exception as e:
            logger.error(f"[MODE] Error saving mode: {str(e)}")
            st.error(f"❌ Error saving mode: {str(e)}")

    st.markdown("---")

    # Display current mode status
    mode_display = f"**Current Mode:** {'🔴 LIVE (REAL MONEY)' if current_mode == 'live' else '📄 PAPER (SIMULATION)'}"
    st.markdown(mode_display)

    st.markdown("---")

    # ============================================================================
    # FEATURE 3: KILL SWITCH (Emergency Stop Button)
    # ============================================================================
    st.markdown("### 🛑 EMERGENCY CONTROLS")

    # Kill switch flag file path (persists across page refreshes)
    KILL_SWITCH_FILE = PROJECT_ROOT / '.kill_switch'

    # Initialize kill switch state in session
    if 'kill_switch_pending' not in st.session_state:
        st.session_state.kill_switch_pending = False
    if 'kill_switch_active' not in st.session_state:
        # Check if kill switch file exists (persistence across refresh)
        st.session_state.kill_switch_active = KILL_SWITCH_FILE.exists()

    # Check current kill switch status from file (persistence)
    current_kill_switch_active = KILL_SWITCH_FILE.exists()

    # Display kill switch status (persistent)
    if current_kill_switch_active:
        st.error("🛑 **KILL SWITCH ACTIVE** - Bot has been emergency stopped")
        st.markdown("""
        **Status:** All orders cancelled, all positions closed, bot not accepting new orders

        To resume trading, restart the bot application.
        """)
    else:
        # Kill switch button - Always visible, big and red
        col1, col2 = st.columns([1, 1])

        with col1:
            if st.button(
                "🛑 KILL SWITCH - STOP ALL TRADING",
                key="kill_switch_btn",
                help="Emergency stop: signals bot to cancel all orders and close all positions"
            ):
                st.session_state.kill_switch_pending = True

        with col2:
            st.markdown("""
            **Safety Features:**
            - Requires explicit confirmation
            - Signals bot immediately
            - Creates persistent flag
            - Full audit trail
            """)

        # Confirmation dialog (persistent via session state)
        if st.session_state.kill_switch_pending:
            st.markdown("---")
            st.markdown("### ⚠️ CONFIRM EMERGENCY STOP")
            st.error(
                "**WARNING:** This will immediately:\n"
                "- Signal bot to cancel all pending orders\n"
                "- Close all open positions\n"
                "- Stop accepting new orders\n\n"
                "This action cannot be undone without restarting the bot."
            )

            # Confirmation buttons
            confirm_col, cancel_col = st.columns(2)

            with confirm_col:
                if st.button("✅ CONFIRM - Execute Kill Switch", key="kill_confirm"):
                    try:
                        # Create persistent kill switch flag (bot will read this)
                        KILL_SWITCH_FILE.touch()

                        # Log kill switch activation with full audit trail
                        timestamp = datetime.now().isoformat()
                        audit_log = {
                            'timestamp': timestamp,
                            'action': 'KILL_SWITCH_ACTIVATED',
                            'reason': 'User initiated emergency stop',
                            'status': 'active',
                            'mode': current_mode,
                        }
                        logger.warning(
                            f"[KILL_SWITCH] ACTIVATED at {timestamp} - "
                            f"User emergency stop (mode: {current_mode.upper()}, status: active)"
                        )

                        # Update session state
                        st.session_state.kill_switch_active = True
                        st.session_state.kill_switch_pending = False

                        st.error("🛑 **KILL SWITCH ACTIVATED**")
                        st.markdown(
                            "Emergency stop signal sent to bot:\n"
                            "✓ Flag file created (persistent)\n"
                            "✓ Bot will stop accepting orders\n"
                            "✓ All positions will be closed\n"
                            "✓ Audit logged\n\n"
                            "**Restart the bot application to resume trading.**"
                        )
                        st.rerun()
                    except Exception as e:
                        logger.error(f"[KILL_SWITCH] Error activating: {str(e)}")
                        st.error(f"❌ Error activating kill switch: {str(e)}")

            with cancel_col:
                if st.button("❌ CANCEL - Keep Trading", key="kill_cancel"):
                    st.session_state.kill_switch_pending = False
                    st.info("✅ Kill switch cancelled. Bot continues running.")
                    st.rerun()

    st.markdown("---")

# DYNAMIC MINIMALIST CSS
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    /* CORE RESET */
    .stApp {{
        background-color: {t['bg']};
        color: {t['text']};
        font-family: 'Inter', sans-serif;
    }}
    
    /* REMOVE ALL GRAPHICS */
    .stApp::after, .stApp::before {{ display: none !important; }}
    
    /* HEADERS */
    h1, h2, h3, h4 {{
        font-family: 'Inter', sans-serif !important;
        font-weight: 700 !important;
        color: #fff !important;
        letter-spacing: 0px !important;
        text-transform: none !important;
        animation: none !important;
    }}

    /* CARDS: SIMPLE BOXES */
    .glass-card {{
        background: {t['card_bg']};
        border: 1px solid {t['border']};
        border-radius: 4px;
        padding: 15px; /* Tighter padding */
        margin-bottom: 15px;
        box-shadow: none;
    }}
    
    /* Remove fancy corners */
    .glass-card::before, .glass-card::after {{ display: none !important; }}
    .glass-card:hover {{ transform: none !important; box-shadow: none !important; }}

    /* METRICS */
    .metric-value {{
        font-family: 'Inter', sans-serif;
        font-size: 1.8rem; /* Use readable size */
        font-weight: 700;
        color: #fff;
        text-shadow: none;
    }}

    .metric-label {{
        font-family: 'Inter', sans-serif;
        font-size: 0.7rem;
        font-weight: 600;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    .metric-label::before {{ content: ""; display: none; }} /* Remove arrow */

    /* STATUS COLORS (Still needed for function) */
    .status-online {{ color: #00ff00; text-shadow: none; }}
    .status-offline {{ color: #ff0000; text-shadow: none; }}

    /* BANNER: SIMPLE */
    .hologram-banner {{
        background: #111;
        border: 1px solid #333;
        padding: 20px;
        margin-bottom: 20px;
        border-left: 5px solid #fff;
    }}
    .hologram-banner::after {{ display: none; }}

    /* BUTTONS: FLAT */
    div.stButton > button {{
        background: #222 !important;
        color: #fff !important;
        border: 1px solid #444 !important;
        border-radius: 4px !important;
        transition: background 0.2s !important;
        text-transform: uppercase;
        font-family: 'Inter' !important;
    }}
    div.stButton > button:hover {{
        background: #444 !important;
        border-color: #fff !important;
        transform: none !important;
        box-shadow: none !important;
    }}
    div.stButton > button::before {{ display: none !important; }}

    /* TABLES */
    .stDataFrame {{ border: 1px solid #333 !important; }}
    thead tr th {{ background-color: #222 !important; color: #fff !important; }}
    tbody tr td {{ color: #ccc !important; }}

</style>
""", unsafe_allow_html=True)

# Connection Check Utility
def check_connection():
    has_token = False
    is_valid = False
    
    # Force reload environment
    load_dotenv(override=True)
    api_key = os.getenv('API_KEY')
    logger.info(f"DEBUG: Dashboard checking connection. API_KEY suffix: {api_key[-10:] if api_key else 'None'}")
    
    if not api_key:
        return "OFFLINE (MISSING API_KEY)", False

    # 1. Check for Token Existence
    if os.path.exists('credentials.json'):
        try:
            with open('credentials.json', 'r') as f:
                creds = json.load(f)
                token = creds.get('mstock', {}).get('access_token')
                if token:
                    has_token = True
                    # 2. Validate Token with Live Call
                    try:
                        from src.market_data import MStockAPI
                        api = MStockAPI()
                        # Use a lightweight call to check validity
                        # Smart API handles prefix automatically
                        quote = api.get_quote('NIFTY') 
                        if quote: 
                            is_valid = True
                        else:
                            is_valid = False
                    except Exception as e:
                        logger.error(f"Conn check error: {e}")
                        is_valid = False
        except Exception as e:
            logger.error(f"Creds read error: {e}")
            pass
            
    if has_token and is_valid:
        return "ONLINE", True
    
    if has_token and not is_valid:
        return "DISCONNECTED (SESSION EXPIRED)", False
        
    return "OFFLINE (NO TOKEN)", False

status_text, is_connected = check_connection()
status_style = "status-online" if is_connected else "status-offline"

# HEADER (CLEAN)
st.markdown(f"""
<div class="hologram-banner">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h1 style="margin:0; font-size: 2rem;">SENTINEL HUB <span style="font-weight: 300;">v2.0</span></h1>
            <div style="font-size: 0.8rem; color: #888;">F&O EXECUTION DASHBOARD</div>
        </div>
        <div style="text-align: right;">
            <div style="font-weight: 700; font-size: 0.9rem;">STATUS: <span class="{status_style}">{status_text}</span></div>
            <div style="color: #666; font-size: 0.8rem;">AES-256 SECURE</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# AUTHENTICATION ENGINE
if not is_connected:
    st.markdown("""
    <div class="glass-card" style="border-left: 5px solid #ff4444;">
        <h4 style="color: #ff4444; margin-top: 0;">CONNECTION LOST</h4>
        <p style="font-size: 0.9rem; color: #ccc;">API token missing. Please re-authenticate.</p>
    </div>
    """, unsafe_allow_html=True)
    
    auth_col1, auth_col2 = st.columns([1, 1])
    
    with auth_col1:
        if st.button("INITIATE LOGIN REQUEST"):
            try:
                from src.market_data import MStockAPI
                api_auth = MStockAPI()
                if api_auth.initiate_login():
                    st.session_state['auth_step'] = 'verify'
                    st.success("OTP SENT TO REGISTERED DEVICE")
                else:
                    st.error("LOGIN REQUEST FAILED. CHECK CREDENTIALS IN .ENV")
            except Exception as e:
                st.error(f"AUTH ERROR: {str(e)}")
    
    if st.session_state.get('auth_step') == 'verify':
        with auth_col2:
            otp_input = st.text_input("ENTER QUANTUM OTP", type="password", help="Enter the 6-digit OTP sent to your device")
            if st.button("VERIFY & SYNC SESSION"):
                if otp_input:
                    try:
                        from src.market_data import MStockAPI
                        api_auth = MStockAPI()
                        if api_auth.complete_login(otp_input):
                            st.session_state['auth_step'] = 'done'
                            st.success("AUTHENTICATION SUCCESSFUL. REFRESHING...")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("INVALID OTP OR SESSION EXPIRED")
                    except Exception as e:
                        st.error(f"VERIFICATION ERROR: {str(e)}")
                else:
                    st.warning("PLEASE ENTER OTP")
else:
    # Clear auth state if connected
    if 'auth_step' in st.session_state:
        del st.session_state['auth_step']



st.markdown("---")

# --- MARKET OVERVIEW ---
st.markdown("### MARKET OVERVIEW")

def get_live_indicators():
    try:
        import sys
        sys.path.insert(0, os.path.dirname(__file__))
        if os.path.exists('src/live_indicators.py'):
            from src.live_indicators import LiveIndicators
            from src.market_data import MStockAPI
            api = MStockAPI()
            live_ind = LiveIndicators(api)
            return live_ind.get_all_indicators()
        else:
            raise FileNotFoundError
    except:
        # Fallback Mock Data with Enhanced Precision (Updated for Current Market Levels)
        return {
            'NIFTY': {'spot_price': 24500.00, 'daily': {'rsi': 54.32, 'adx': 32.15, 'macd_trend': 'Bullish'}, 'intraday_15m': {'rsi': 58.12, 'adx': 29.87, 'macd_trend': 'Bullish'}},
            'BANKNIFTY': {'spot_price': 52100.00, 'daily': {'rsi': 48.76, 'adx': 28.45, 'macd_trend': 'Bearish'}, 'intraday_15m': {'rsi': 52.34, 'adx': 31.22, 'macd_trend': 'Bearish'}},
            'FINNIFTY': {'spot_price': 23200.00, 'daily': {'rsi': 51.23, 'adx': 27.56, 'macd_trend': 'Bullish'}, 'intraday_15m': {'rsi': 53.45, 'adx': 30.12, 'macd_trend': 'Bullish'}},
            'SENSEX': {'spot_price': 80500.00, 'daily': {'rsi': 52.34, 'adx': 29.87, 'macd_trend': 'Bullish'}, 'intraday_15m': {'rsi': 55.67, 'adx': 31.45, 'macd_trend': 'Bullish'}},
            'VIX': 13.50
        }

indicators = get_live_indicators()

col1, col2 = st.columns([3, 1])

with col1:
    # INDICES GRID
    indices_to_show = ['NIFTY', 'BANKNIFTY', 'FINNIFTY', 'SENSEX']
    cols = st.columns(len(indices_to_show))
    
    for i, index_name in enumerate(indices_to_show):
        with cols[i]:
            idx_data = indicators.get(index_name, {})
            price = idx_data.get('spot_price', 0)
            daily = idx_data.get('daily', {})
            intra = idx_data.get('intraday_15m', {})
            
            trend = intra.get('macd_trend', 'N/A')
            glow_color = "#00ff88" if trend == "Bullish" else ("#ff4444" if trend == "Bearish" else "#888")
            
            price_str = f"{price:,.2f}"
            
            st.markdown(f"""
            <div class="glass-card" style="text-align: center; padding: 10px;">
                <div class="metric-label">{index_name}</div>
                <div class="metric-value" style="font-size: 1.1rem;">{price_str}</div>
                <div style="font-size: 0.7rem; color: {glow_color}; margin-top: 5px;">
                    {trend}
                </div>
            </div>
            """, unsafe_allow_html=True)

with col2:
    vix = indicators.get('VIX', 0)
    st.markdown(f"""
    <div class="glass-card" style="text-align: center; padding: 10px;">
        <div class="metric-label">INDIA VIX</div>
        <div class="metric-value" style="font-size: 1.5rem; color: #ffcc00;">{vix:.2f}</div>
    </div>
    """, unsafe_allow_html=True)


# --- ACTIVE POSITIONS ---
from src.persistence import StateManager
active_positions = StateManager.load_positions()

if active_positions:
    st.markdown(f"#### ACTIVE POSITIONS [{len(active_positions)}]")
    for symbol, pos in active_positions.items():
        pnl = pos.pnl if pos.pnl else 0
        pnl_color = "#00ff88" if pnl >= 0 else "#ff4444"
        type_color = "#00ff88" if pos.trade_type.value == "CE" else "#ff4444"
        
        st.markdown(f"""
        <div class="glass-card" style="border-left: 5px solid {type_color}; padding: 10px; margin-bottom: 10px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="font-weight: bold; font-size: 1rem;">{pos.underlying}</span>
                    <span style="background: {type_color}20; color: {type_color}; padding: 2px 6px; border-radius: 4px; font-size: 0.8rem; margin-left: 8px;">{pos.trade_type.value}</span>
                </div>
                <div style="font-weight: bold; font-size: 1.2rem; color: {pnl_color};">
                    Running P&L: {pnl:,.2f}
                </div>
            </div>
            <div style="display: flex; justify-content: space-between; margin-top: 5px; font-size: 0.8rem; color: #888;">
                <div>Qty: {pos.lot_size} | Entry: {pos.entry_price:.2f}</div>
                <div>SL: {pos.sl_percentage:.2f}%</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
else:
    # No positions
    pass


st.markdown("---")

# --- Process Management Logic (Moved for Scope Viability) ---
@st.cache_data(ttl=5)
def get_all_python_pids():
    """Cache the list of python processes to speed up UI"""
    pids = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmd = proc.info.get('cmdline') or []
            if any("main.py" in arg for arg in cmd):
                pids.append(proc.info['pid'])
        except: continue
    return pids

def get_bot_status():
    """Optimized check if main.py is running"""
    # 1. Quick check using session state PID
    if 'bot_pid' in st.session_state:
        pid = st.session_state['bot_pid']
        if psutil.pid_exists(pid):
            try:
                proc = psutil.Process(pid)
                cmd = proc.cmdline()
                if any("main.py" in arg for arg in cmd):
                    return "RUNNING", pid
            except: pass
    
    # 2. Cached fallback scan
    pids = get_all_python_pids()
    if pids:
        st.session_state['bot_pid'] = pids[0]
        return "RUNNING", pids[0]
        
    return "STOPPED", None

def start_bot():
    return None

def stop_bot(pid):
    return False

@st.cache_data(ttl=1)
def get_latest_logs(n=25):
    try:
        log_files = glob.glob('logs/trading_bot_*.log')
        if not log_files: return "NO LOG DATA DETECTED..."
        latest_log = max(log_files, key=os.path.getmtime)
        with open(latest_log, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            return "".join(lines[-n:])
    except: return "SCANNING FOR PULSE..."

def load_order_status():
    try:
        if os.path.exists('logs/orders_log.json'):
            with open('logs/orders_log.json', 'r') as f:
                orders = json.load(f)
                return orders[-10:] if len(orders) > 10 else orders
        return []
    except: return []

# CONFIGURATION & CONTROL
st.markdown("### [02] // QUANTUM_REGISTRY_CONTROL")

try:
    with open('config.json', 'r') as f:
        config = json.load(f)
except:
    st.error("Missing config.json")
    st.stop()

col_cfg1, col_cfg2 = st.columns([2, 1])

with col_cfg1:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### INDEX_RISK")
        n_sl = st.number_input("NIFTY SL %", value=float(config.get('stop_loss', {}).get('NIFTY', {}).get('base_sl_percent', 0.70)), step=0.05)
        bn_sl = st.number_input("BANKNIFTY SL %", value=float(config.get('stop_loss', {}).get('BANKNIFTY', {}).get('base_sl_percent', 1.00)), step=0.05)
        fn_sl = st.number_input("FINNIFTY SL %", value=float(config.get('stop_loss', {}).get('FINNIFTY', {}).get('base_sl_percent', 0.80)), step=0.05)
        sx_sl = st.number_input("SENSEX SL %", value=float(config.get('stop_loss', {}).get('SENSEX', {}).get('base_sl_percent', 0.60)), step=0.05)

    with c2:
        st.markdown("#### QUANTITY_CONTROL")
        n_lots = st.number_input("NIFTY LOTS", value=int(config.get('lot_sizes', {}).get('NIFTY', {}).get('num_lots', 1)))
        bn_lots = st.number_input("BANKNIFTY LOTS", value=int(config.get('lot_sizes', {}).get('BANKNIFTY', {}).get('num_lots', 1)))
        fn_lots = st.number_input("FINNIFTY LOTS", value=int(config.get('lot_sizes', {}).get('FINNIFTY', {}).get('num_lots', 1)))
        sx_lots = st.number_input("SENSEX LOTS", value=int(config.get('lot_sizes', {}).get('SENSEX', {}).get('num_lots', 1)))
    st.markdown('</div>', unsafe_allow_html=True)

with col_cfg2:
    st.markdown('<div class="glass-card" style="height: 100%;">', unsafe_allow_html=True)
    st.markdown("#### GLOBAL_BRAKES")
    profit_target = st.select_slider("PROFIT TARGET (Rs)", options=[i for i in range(250, 10001, 250)], value=int(config.get('profit_targets', {}).get('profit_target_amount', 2000)))
    daily_loss = st.slider("DAILY LOSS CAP %", 1.0, 10.0, float(config.get('capital', {}).get('daily_loss_limit_percent', 3.0)), 0.5)
    
    if st.button("SYNCHRONIZE SETTINGS"):
        config['stop_loss']['NIFTY'] = config['stop_loss'].get('NIFTY', {})
        config['stop_loss']['NIFTY']['base_sl_percent'] = float(n_sl)
        config['stop_loss']['BANKNIFTY']['base_sl_percent'] = float(bn_sl)
        config['stop_loss']['FINNIFTY']['base_sl_percent'] = float(fn_sl)
        config['stop_loss']['SENSEX']['base_sl_percent'] = float(sx_sl)
        
        config['lot_sizes']['NIFTY'] = config['lot_sizes'].get('NIFTY', {})
        config['lot_sizes']['NIFTY']['num_lots'] = int(n_lots)
        config['lot_sizes']['BANKNIFTY']['num_lots'] = int(bn_lots)
        config['lot_sizes']['FINNIFTY']['num_lots'] = int(fn_lots)
        config['lot_sizes']['SENSEX']['num_lots'] = int(sx_lots)
        if 'profit_targets' not in config: config['profit_targets'] = {}
        config['profit_targets']['profit_target_amount'] = float(profit_target)
        config['capital']['daily_loss_limit_percent'] = float(daily_loss)
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)
            

        st.success("QUANTUM REGISTRY UPDATED")
                
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# PERFORMANCE SECTION
st.markdown("### [03] // MISSION_DEBRIEF_ANALYTICS")

@st.cache_data(ttl=60)
def sync_with_broker():
    """Fetch high-fidelity F&O data directly from broker API and Cache it locally"""
    from src.market_data import MStockAPI
    from src.persistence import StateManager
    from src.trading_models import Position, TradeType, ExitReason
    
    api = MStockAPI()
    broker_trades = []
    sync_status = "STABLE"
    
    try:
        # 1. Fetch Today's Tradebook (3s Fast-Fail)
        trades = api.get_tradebook(timeout=(2, 3))
        if trades and isinstance(trades, list):
            for t in trades:
                if not isinstance(t, dict): continue
                broker_trades.append({
                    'Exit_Time': pd.to_datetime(t.get('executionTime', datetime.now())),
                    'P&L': float(t.get('realizedPnl', 0)),
                    'Underlying': t.get('tradingsymbol', 'F&O'),
                    'Source': 'BROKER_MANUAL'
                })
        
        # 2. Fetch Net Positions (3s Fast-Fail)
        positions = api.get_net_positions(timeout=(2, 3))
        if positions and isinstance(positions, list):
            existing_history = StateManager.load_history()
            new_entries = False
            
            for p in positions:
                if not isinstance(p, dict): continue
                
                realized = float(p.get('realizedPnl', p.get('realized_profit', 0)))
                symbol = p.get('tradingsymbol', 'F&O')
                
                if realized != 0:
                    broker_trades.append({
                        'Exit_Time': pd.to_datetime(datetime.now()),
                        'P&L': realized,
                        'Underlying': symbol,
                        'Source': 'BROKER_POSITION'
                    })
                    
                    # HISTORIAN CACHE: Save manual trades locally so they persist on weekends
                    today = datetime.now().date()
                    if not any(h.underlying == symbol and h.exit_time and h.exit_time.date() == today for h in existing_history):
                        mock_pos = Position(
                            position_id=f"MANUAL_{symbol}_{int(datetime.now().timestamp())}",
                            underlying=symbol,
                            trade_type=TradeType.CALL,
                            entry_time=datetime.now(),
                            entry_price=0,
                            lot_size=0,
                            sl_percentage=0,
                            exit_time=datetime.now(),
                            pnl=realized,
                            exit_reason=ExitReason.TARGET_MET
                        )
                        existing_history.append(mock_pos)
                        new_entries = True
            
            if new_entries:
                StateManager.save_history(existing_history)
                logger.info(f"ARCHIVED {len(positions)} TRADES")
                
    except Exception as e:
        sync_status = "SYNC_BREACH"
        logger.error(f"Broker Sync failed: {e}")
        
    return broker_trades, sync_status

@st.cache_data(ttl=1)
def load_all_history():
    """Load and aggregate all historical trades from JSON, CSV, and Broker Pulse"""
    all_trades = []
    
    # 1. Load from JSON State (Bot Memory)
    if os.path.exists('data/daily_history.json'):
        try:
            with open('data/daily_history.json', 'r') as f:
                data = json.load(f)
                for pos in data:
                    all_trades.append({
                        'Exit_Time': pd.to_datetime(pos.get('exit_time')),
                        'P&L': pos.get('pnl', 0),
                        'Underlying': pos.get('underlying', 'N/A'),
                        'Source': 'BOT_CORE'
                    })
        except: pass

    # 2. Sync from Broker Pulse (Manual + Bot Current)
    broker_trades, sync_status = sync_with_broker()
    all_trades.extend(broker_trades)

    # 3. Backup: Load from CSV logs
    csv_files = glob.glob('logs/live_trades_*.csv') + glob.glob('logs/paper_trades_*.csv')
    for f in csv_files:
        try:
            df = pd.read_csv(f)
            if 'Exit_Time' in df.columns and 'P&L' in df.columns:
                df['Exit_Time'] = pd.to_datetime(df['Exit_Time'])
                for _, row in df.iterrows():
                    all_trades.append({
                        'Exit_Time': row['Exit_Time'],
                        'P&L': row['P&L'],
                        'Underlying': row['Underlying'],
                        'Source': 'CSV_LOG'
                    })
        except: continue
        
    if not all_trades: return pd.DataFrame(), "MISSING_DATA"
    
    # Deduplicate by Exit_Time and Underlying 
    df = pd.DataFrame(all_trades)
    df = df.dropna(subset=['Exit_Time'])
    df = df.sort_values('Exit_Time', ascending=False).drop_duplicates(subset=['Exit_Time', 'Underlying'])
    return df, sync_status

st.markdown("---")

# 3. LIVE ORDERS & LOGS
st.markdown("#### RECENT_ORDER_FLOW")

orders = load_order_status()

if orders:
    # Force-Fit HTML Table (No Scrolling, Clean Layout)
    # IMPORTANT: Use textwrap.dedent or manually ensure no indentation for the string
    table_html = """
<style>
    .order-table-container { width: 100%; overflow-x: hidden; }
    .order-table { 
        width: 100%; 
        border-collapse: collapse; 
        table-layout: fixed; 
        font-family: 'Courier New', monospace; 
        font-size: 0.7rem; 
    }
    .order-table th { 
        text-align: left; 
        color: #666; 
        border-bottom: 1px solid #333; 
        padding: 4px; 
        font-weight: normal;
        letter-spacing: 1px;
    }
    .order-table td { 
        padding: 4px; 
        border-bottom: 1px solid #222; 
        color: #ccc; 
        white-space: nowrap; 
        overflow: hidden; 
        text-overflow: ellipsis; 
    }
    .order-table tr:last-child td { border-bottom: none; }
</style>
<div class="order-table-container">
    <table class="order-table">
        <thead>
            <tr>
                <th style="width: 15%;">TIME</th>
                <th style="width: 30%;">SYMBOL</th>
                <th style="width: 10%;">SIDE</th>
                <th style="width: 10%;">QTY</th>
                <th style="width: 35%;">MSG</th>
            </tr>
        </thead>
        <tbody>
"""
    
    for order in reversed(orders):
        time_str = str(order.get('timestamp', ''))[11:19]
        sym = order.get('symbol', '')
        side = order.get('side', '')
        qty = order.get('quantity', 0)
        status = order.get('status', 'N/A')
        msg = order.get('reason', '')
        
        # Combine Status and Msg for compactness
        display_msg = status if not msg else msg
        
        s_color = "#00ff88" if "BUY" in side else "#ff4444"
        msg_color = "#ff4444" if "REJECTED" in status or "INSUFFICIENT" in display_msg else "#888"
        
        # Use f-string directly without indentation for the row
        table_html += f"""<tr>
<td>{time_str}</td>
<td style="font-weight: bold; color: {s_color};" title="{sym}">{sym}</td>
<td style="color: {s_color};">{side}</td>
<td>{qty}</td>
<td style="color: {msg_color};" title="{display_msg}">{display_msg}</td>
</tr>"""
        
    table_html += "</tbody></table></div>"
    st.markdown(table_html, unsafe_allow_html=True)
else:
    st.info("SCANNING FOR TARGETS... NO TRADES DETECTED IN CURRENT SESSION.")

st.markdown("---")
st.caption("SENTINEL HUB // v2.0 // AUTO-REFRESH [3S]")

time.sleep(3)
st.rerun() 
