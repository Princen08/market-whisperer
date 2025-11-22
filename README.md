# Market Whisperer

**Market Whisperer** is a real-time stock analysis tool that combines live news, historical market data, and AI-powered reasoning to provide actionable trading insights.

![Market Whisperer UI](backend/static/screenshot_placeholder.png)

## Features

- **Real-Time News**: Fetches the latest headlines from major financial sources (Reuters, Bloomberg, Moneycontrol, etc.) via Google News.
- **AI Analysis**: Uses **Google Gemini 1.5 Flash** to analyze news sentiment and relevance in real-time.
- **Context-Aware**: Integrates **30-day historical market data** (Price, Volume, Volatility) using `yfinance` to give smarter, context-aware recommendations.
- **Smart Signals**: Provides clear **BUY**, **SELL**, or **HOLD** signals with AI-generated reasoning.
- **High Performance**:
  - **Asynchronous Processing**: Uses **Celery** & **Redis** to handle background tasks without blocking the UI.
  - **Parallel Execution**: Analyzes multiple stocks concurrently for instant results.
  - **Batch Processing**: Optimizes AI API calls for speed and efficiency.
- **Premium UI**: A modern, dark-themed interface with glassmorphism design.

## Tech Stack

- **Backend**: Python (FastAPI)
- **AI Engine**: Google Gemini (via `google-generativeai`)
- **Market Data**: `yfinance`, `feedparser`
- **Task Queue**: Celery + Redis
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Deployment**: Docker (Optional), Local Venv

## Setup & Installation

### Prerequisites
- Python 3.9+
- Redis (for Celery)
- Google Gemini API Key

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/market-whisperer.git
cd market-whisperer
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 4. Configure Environment
Set your Gemini API Key:
```bash
export GEMINI_API_KEY="your_api_key_here"
```

### 5. Start Redis
Ensure Redis is running locally:
```bash
redis-server
```

## Running the App

You need to run the Backend API and the Celery Worker in separate terminals.

**Terminal 1: FastAPI Backend**
```bash
source venv/bin/activate
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2: Celery Worker**
```bash
source venv/bin/activate
export GEMINI_API_KEY="your_api_key_here"
celery -A backend.celery_worker.celery_app worker --loglevel=info --pool=threads
```

Open your browser and go to: `http://localhost:8000`

## Usage

1.  **Add Stocks**: Enter a stock symbol (e.g., `AAPL`, `RELIANCE`, `TCS`) and press Enter.
2.  **Listen**: Click the **"LISTEN TO THE MARKET"** button.
3.  **Analyze**: The app will fetch news, analyze market context, and display AI-generated insights in real-time.

## Project Structure

```
market-whisperer/
├── backend/
│   ├── static/          # Frontend assets (HTML, CSS, JS)
│   ├── analyzer.py      # Core logic (News Fetcher, Market Data, LLM)
│   ├── celery_worker.py # Celery task configuration
│   ├── main.py          # FastAPI application
│   ├── market_data.py   # yfinance integration
│   ├── models.py        # Pydantic models
│   └── requirements.txt # Python dependencies
└── README.md
```

## Contributing

Contributions are welcome! Please fork the repository and submit a Pull Request.

## License

MIT License.
