"""
External Watchdog - Dead-Man's-Switch for bot process monitoring
Sends periodic heartbeats to external service; absence triggers alert

Author: Antigravity Bot
Date: 2026-06-23
"""

import os
import logging
import threading
import time
import requests
from datetime import datetime

logger = logging.getLogger(__name__)


class ExternalWatchdog:
    """
    External watchdog sends periodic heartbeats to verify bot is alive.
    If heartbeat stops, external service raises alert (SMS/Telegram).

    Bug #21 Fix: Monitors bot via external service, not just in-process
    """

    def __init__(self, heartbeat_interval: int = 60):
        """
        Initialize external watchdog

        Parameters:
        -----------
        heartbeat_interval : int
            Seconds between heartbeats (default 60 seconds)
        """
        self.heartbeat_interval = heartbeat_interval
        self.enabled = os.getenv("ENABLE_EXTERNAL_WATCHDOG", "false").lower() == "true"
        self.watchdog_url = os.getenv("WATCHDOG_URL", "")  # e.g. https://uptime.example.com/ping/abc123
        self.running = False
        self.thread = None

    def start(self):
        """Start external watchdog thread"""
        if not self.enabled or not self.watchdog_url:
            logger.info("External watchdog disabled (set ENABLE_EXTERNAL_WATCHDOG=true and WATCHDOG_URL env vars)")
            return

        self.running = True
        self.thread = threading.Thread(target=self._heartbeat_loop, daemon=True, name="ExternalWatchdog")
        self.thread.start()
        logger.info(f"External watchdog started (heartbeat every {self.heartbeat_interval}s)")

    def stop(self):
        """Stop external watchdog thread"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("External watchdog stopped")

    def _heartbeat_loop(self):
        """Periodic heartbeat loop"""
        while self.running:
            try:
                self._send_heartbeat()
            except Exception as e:
                logger.warning(f"Heartbeat failed: {e}")
            time.sleep(self.heartbeat_interval)

    def _send_heartbeat(self):
        """Send heartbeat to external service"""
        try:
            payload = {
                "status": "alive",
                "timestamp": datetime.now().isoformat(),
                "bot_name": "antigravity_trading_bot"
            }

            response = requests.post(
                self.watchdog_url,
                json=payload,
                timeout=5
            )

            if response.status_code == 200:
                logger.debug(f"Heartbeat sent successfully")
            else:
                logger.warning(f"Heartbeat returned {response.status_code}")

        except Exception as e:
            logger.debug(f"Error sending heartbeat: {e}")

    @staticmethod
    def configure_from_env():
        """Create watchdog configured from environment variables"""
        interval = int(os.getenv("WATCHDOG_INTERVAL", "60"))
        return ExternalWatchdog(heartbeat_interval=interval)


# Singleton instance
_watchdog_instance = None


def get_external_watchdog() -> ExternalWatchdog:
    """Get or create external watchdog singleton"""
    global _watchdog_instance
    if _watchdog_instance is None:
        _watchdog_instance = ExternalWatchdog.configure_from_env()
    return _watchdog_instance
