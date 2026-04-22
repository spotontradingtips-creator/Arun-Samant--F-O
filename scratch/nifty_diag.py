from src.api.main_api import MStockAPI
import logging

logging.basicConfig(level=logging.INFO)
api = MStockAPI()
if api.ensure_session_is_valid():
    print("Session Valid.")
    # Check Nifty
    print("Fetching NIFTY 50...")
    nifty = api.get_quote("NIFTY 50", "NSE")
    print(f"NIFTY 50 Result: {nifty}")
    
    # Check BankNifty
    print("\nFetching NIFTY BANK...")
    bn = api.get_quote("NIFTY BANK", "NSE")
    print(f"BANKNIFTY Result: {bn}")

    # Check Sensex
    print("\nFetching SENSEX...")
    sensex = api.get_get_quote("SENSEX", "BSE") # Note: Sensex uses BSE usually
    print(f"SENSEX Result: {sensex}")
