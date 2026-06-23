"""
OTP Manager - Coordinates remote OTP entry via Telegram
"""

import os
import json
import time
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Define Project Root for Absolute Path Resolution
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REQUEST_FILE = os.path.join(PROJECT_ROOT, "data", "otp_request.json")
RESPONSE_FILE = os.path.join(PROJECT_ROOT, "data", "otp_response.json")

class OTPManager:
    @staticmethod
    def request_otp(timeout_mins: int = 5) -> str:
        """
        Signals that an OTP is required and waits for a response.
        Called by main.py / MStockAPI
        """
        os.makedirs("data", exist_ok=True)

        # 1. Create Request
        request_data = {
            "status": "PENDING",
            "timestamp": datetime.now().isoformat(),
            "message": "OTP Required for M-Stock Login"
        }

        with open(REQUEST_FILE, 'w') as f:
            json.dump(request_data, f, indent=4)

        logger.info(f"OTP Request signaled. Waiting for user to send it via Telegram ({timeout_mins}m timeout)...")

        try:
            # 2. Poll for Response
            start_time = time.time()
            timeout_secs = timeout_mins * 60

            while (time.time() - start_time) < timeout_secs:
                if os.path.exists(RESPONSE_FILE):
                    try:
                        with open(RESPONSE_FILE, 'r') as f:
                            response = json.load(f)

                        otp = response.get("otp")
                        if otp:
                            logger.info("OTP received from Telegram response file!")
                            return str(otp)
                    except Exception as e:
                        logger.error(f"Error reading OTP response: {e}")

                time.sleep(2)

            logger.warning("OTP Request timed out.")
            return None
        finally:
            # Bug #17 Fix: Always clean up OTP files, even on timeout or error
            if os.path.exists(REQUEST_FILE):
                try:
                    os.remove(REQUEST_FILE)
                except Exception as e:
                    logger.warning(f"Failed to delete OTP request file: {e}")
            if os.path.exists(RESPONSE_FILE):
                try:
                    os.remove(RESPONSE_FILE)
                except Exception as e:
                    logger.warning(f"Failed to delete OTP response file: {e}")

    @staticmethod
    def check_for_pending_request() -> bool:
        """Checks if there is an active OTP request"""
        return os.path.exists(REQUEST_FILE)

    @staticmethod
    def provide_otp(otp: str):
        """
        Writes the OTP to the response file.
        Called by telegram_bot.py
        """
        os.makedirs("data", exist_ok=True)
        response_data = {
            "otp": otp,
            "timestamp": datetime.now().isoformat()
        }
        with open(RESPONSE_FILE, 'w') as f:
            json.dump(response_data, f, indent=4)
        logger.info("OTP written to response file.")
