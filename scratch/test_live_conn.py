from src.market_data import MStockAPI
import logging

logging.basicConfig(level=logging.INFO)

def test_connection():
    api = MStockAPI()
    print(f"Current Token: {api.access_token[:10]}... if exists")
    is_valid = api.ensure_session_is_valid()
    print(f"Session Valid: {is_valid}")
    if is_valid:
        quote = api.get_quote("NIFTY", "NSE")
        print(f"NIFTY Quote: {quote}")

if __name__ == "__main__":
    test_connection()
