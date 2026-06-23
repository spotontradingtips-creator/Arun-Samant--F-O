"""
Manual Buy / Auto Sell Sentinel
Continuously monitors positions and places a +7 limit sell immediately.
"""

import time
import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

from src.market_data import MStockAPI
from src.utils import setup_logging, console

os.makedirs("logs", exist_ok=True)
log_file = f"logs/auto_sell_bot_{datetime.now().strftime('%Y%m%d')}.log"
logger = setup_logging(log_file)

def run_auto_sell():
    api = MStockAPI()
    
    # Connect and Authenticate
    if not api.ensure_session_is_valid():
        logger.error("Failed to authenticate with broker.")
        return

    logger.info("========================================")
    logger.info("   AUTO-SELL SENTINEL ACTIVATED         ")
    logger.info("   Mode: Manual Buy Only                ")
    logger.info("   Target: +7 Points Limit Sell         ")
    logger.info("   Speed: 200ms Polling Loop            ")
    logger.info("========================================")

    # Memory to prevent duplicate sell orders
    # Mapping of symbol -> netQuantity
    processed_positions = {}

    while True:
        try:
            # Reconnect if session expires
            if not api.ensure_session_is_valid():
                logger.warning("Session invalid. Reconnecting...")
                time.sleep(2)
                continue

            # 1. Fetch Net Positions
            positions = api.get_net_positions(timeout=(5, 10))
            if positions is None:
                # Minor sleep to prevent rapid failing loops
                time.sleep(0.5)
                continue

            current_active = {}
            for pos in positions:
                symbol = pos.get('tradingsymbol')
                exchange = pos.get('exchange', 'NFO')
                qty = pos.get('quantity', 0)
                if qty == 0:
                    qty = pos.get('netQuantity', 0)
                
                # Check for open buy position (Positive quantity means long position)
                if qty > 0 and exchange in ['NFO', 'BFO', 'NSE', 'BSE']:
                    current_active[symbol] = {
                        'qty': qty,
                        'price': pos.get('averagePrice', pos.get('avgPrice', 0.0)),
                        'exchange': exchange
                    }

            # 2. Process active positions
            for symbol, data in current_active.items():
                qty = data['qty']
                avg_price = data['price']
                exchange = data['exchange']

                # Check if we already processed this position size
                if symbol not in processed_positions or processed_positions[symbol] != qty:
                    
                    target_price = round(avg_price + 7.0, 2)
                    logger.info(f"[TRIGGER] Buy confirmed for {symbol} | Qty: {qty} | Avg Price: {avg_price} | Target: {target_price}")
                    
                    # Place Limit Sell Order
                    order_id = api.place_order(
                        symbol=symbol,
                        exchange=exchange,
                        qty=qty,
                        side='SELL',
                        order_type='LIMIT',
                        price=target_price,
                        paper_mode=False
                    )

                    if order_id:
                        logger.info(f"[SUCCESS] Sell Limit placed @ {target_price} (Order ID: {order_id})")
                        processed_positions[symbol] = qty
                    else:
                        logger.error(f"[FAILED] Could not place sell order for {symbol}")

            # 3. Cleanup processed memory for closed positions
            # If position quantity dropped to 0 (sold), we can remove it from memory
            # next time they buy, qty > 0 again.
            symbols_to_remove = []
            for processed_sym in processed_positions:
                if processed_sym not in current_active:
                    symbols_to_remove.append(processed_sym)
            
            for sym in symbols_to_remove:
                logger.info(f"[CLEARED] Position closed for {sym}. Ready for next trade.")
                del processed_positions[sym]

        except Exception as e:
            logger.error(f"Error in monitor loop: {e}")
        
        # 200ms Sleep to maintain speed requirement
        time.sleep(0.2)

if __name__ == "__main__":
    try:
        run_auto_sell()
    except KeyboardInterrupt:
        logger.info("Auto-Sell Sentinel stopped by user.")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
