import logging
import sys
import os

# Ensure the root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.market_data import MStockAPI, IPMismatchError

# Setup logging to see the details
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_connection():
    try:
        api = MStockAPI()
        logger.info("Testing connection to mStock API...")
        
        # Test 1: Session validation
        if api.ensure_session_is_valid():
            logger.info("[OK] Session is valid.")
        else:
            logger.error("[FAIL] Session invalid. Authentication check failed.")
            return

        # Test 2: Portfolio/Positions (Holiday-proof test)
        logger.info("Attempting to fetch net positions (Holiday-proof test)...")
        positions = api.get_net_positions()
        if positions is not None:
             logger.info(f"[SUCCESS] Core API connection verified! IP is valid in mStock portal.")
             logger.info(f"Retrieved {len(positions)} positions data (even if empty).")
        else:
             logger.error("[FAIL] API connected but positions fetch failed. Could be holiday-related status, but IP mismatch was NOT triggered.")

    except IPMismatchError as e:
        logger.critical(f"[FATAL] IP Mismatch! The mStock portal update is NOT working yet. Error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during verification: {e}")

if __name__ == "__main__":
    verify_connection()
