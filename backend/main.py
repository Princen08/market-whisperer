from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from backend.models import Stock
from backend.analyzer import MarketAnalyzer

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(title="Market Whisperer API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="backend/static"), name="static")

analyzer = MarketAnalyzer()
from backend.celery_worker import analyze_stocks_task, celery_app
from celery.result import AsyncResult

# In-memory storage for demo purposes
tracked_stocks: List[Stock] = []

@app.get("/")
async def read_root():
    return FileResponse('backend/static/index.html')

@app.get("/stocks", response_model=List[Stock])
def get_stocks():
    return tracked_stocks

@app.post("/stocks", response_model=Stock)
def add_stock(stock: Stock):
    # Check if already exists
    if any(s.symbol == stock.symbol for s in tracked_stocks):
        raise HTTPException(status_code=400, detail="Stock already tracked")
    tracked_stocks.append(stock)
    return stock

@app.delete("/stocks/{symbol}")
def remove_stock(symbol: str):
    global tracked_stocks
    tracked_stocks = [s for s in tracked_stocks if s.symbol != symbol]
    return {"message": "Stock removed"}

@app.post("/analyze/start")
def start_analysis():
    # Pass stocks as dicts to be serializable
    stocks_data = [s.dict() for s in tracked_stocks]
    task = analyze_stocks_task.delay(stocks_data)
    return {"task_id": task.id}

@app.get("/analyze/status/{task_id}")
def get_analysis_status(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)
    if task_result.state == 'PENDING':
        return {"state": "PENDING", "status": "Analysis in progress..."}
    elif task_result.state != 'FAILURE':
        return {
            "state": task_result.state,
            "result": task_result.result
        }
    else:
        return {
            "state": "FAILURE",
            "error": str(task_result.info)
        }
