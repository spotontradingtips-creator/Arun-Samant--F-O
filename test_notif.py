import os
import sys
import logging
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.notifications import notify_system_status

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("Testing Telegram Notification...")
try:
    notify_system_status(True, "TEST ALERT")
    print("Notification sent (check Telegram).")
except Exception as e:
    print(f"FAILED: {e}")
