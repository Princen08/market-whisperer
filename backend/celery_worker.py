from celery import Celery
from backend.analyzer import MarketAnalyzer
from backend.models import Whisper, Stock
from typing import List

# Initialize Celery
# Broker URL: redis://localhost:6379/0
# Backend URL: redis://localhost:6379/0 (to store results)
celery_app = Celery(
    "market_whisperer",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

analyzer = MarketAnalyzer()

@celery_app.task(bind=True)
def analyze_stocks_task(self, stocks_data: List[dict]):
    # Convert dicts back to Stock objects
    stocks = [Stock(**s) for s in stocks_data]
    
    # Run analysis
    whispers = analyzer.analyze_stocks(stocks)
    
    # Return results as dicts (JSON serializable)
    return [w.dict() for w in whispers]
