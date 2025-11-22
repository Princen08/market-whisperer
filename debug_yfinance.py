from backend.market_data import MarketDataProvider
import sys

print("Starting yfinance debug...")
try:
    provider = MarketDataProvider()
    symbol = "AAPL" # Test with a known symbol
    print(f"Fetching data for {symbol}...")
    context = provider.get_context(symbol)
    print(f"Context received: {context}")
except Exception as e:
    print(f"Error: {e}")
except:
    print("Unexpected error:", sys.exc_info()[0])
print("Finished yfinance debug.")
