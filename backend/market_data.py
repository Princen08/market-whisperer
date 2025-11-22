import yfinance as yf
import pandas as pd

class MarketDataProvider:
    def get_context(self, symbol: str) -> str:
        try:
            # Fetch last 1 month of data
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1mo")
            
            if hist.empty:
                return "No historical data available."

            # Calculate metrics
            current_price = hist['Close'].iloc[-1]
            start_price = hist['Close'].iloc[0]
            price_change_pct = ((current_price - start_price) / start_price) * 100
            
            avg_volume = hist['Volume'].mean()
            current_volume = hist['Volume'].iloc[-1]
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
            
            # Simple volatility (std dev of daily returns)
            daily_returns = hist['Close'].pct_change().dropna()
            volatility = daily_returns.std() * 100 # as percentage

            # Determine trend description
            trend = "SIDEWAYS"
            if price_change_pct > 5: trend = "UPTREND"
            elif price_change_pct < -5: trend = "DOWNTREND"

            volatility_desc = "LOW"
            if volatility > 2: volatility_desc = "HIGH"
            elif volatility > 1: volatility_desc = "MEDIUM"

            context = (
                f"Price Trend (1mo): {trend} ({price_change_pct:.1f}%). "
                f"Volatility: {volatility_desc} ({volatility:.1f}% daily). "
                f"Volume: {volume_ratio:.1f}x average. "
                f"Current Price: {current_price:.2f}."
            )
            return context
        except Exception as e:
            print(f"Error fetching market data for {symbol}: {e}")
            return "Market data unavailable."
