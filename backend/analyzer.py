import feedparser
from textblob import TextBlob
import urllib.parse
from typing import List, Dict, Optional
from backend.models import Stock, Whisper

class NewsFetcher:
    def __init__(self):
        # Removed US-specific params to be more global/Indian friendly
        self.base_url = "https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
        self.keywords = {
            "MERGER": ["merger", "acquisition", "acquire", "takeover"],
            "MOVEMENT": ["surge", "plunge", "soar", "crash", "rally", "tumble", "upper circuit", "lower circuit"],
            "NEWS": ["announce", "launch", "report", "earnings", "revenue", "profit", "loss", "dividend"]
        }
        self.priority_sources = [
            "Reuters", "Bloomberg", "The Ken", "Financial Times", "Wall Street Journal",
            "Moneycontrol", "Economic Times", "Livemint", "Business Standard", "CNBC-TV18"
        ]

    def fetch_news(self, symbol: str) -> List[dict]:
        # Construct query: Symbol + "stock" to be more specific
        query = urllib.parse.quote(f"{symbol} stock")
        url = self.base_url.format(query=query)
        feed = feedparser.parse(url)
        
        articles = []
        for entry in feed.entries[:10]: # Check top 10 stories
            articles.append({
                "title": entry.title,
                "link": entry.link,
                "source": entry.source.title if hasattr(entry, 'source') else "Unknown",
                "published": entry.published
            })
        return articles

import google.generativeai as genai
import os
import json

from .market_data import MarketDataProvider

class LLMAnalyzer:
    def __init__(self):
        # Configure Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("WARNING: GEMINI_API_KEY not found. Using mock/fallback.")
            self.model = None
        else:
            genai.configure(api_key=api_key)
            # Updated to a model name explicitly found in the list
            self.model = genai.GenerativeModel('gemini-flash-latest')

    def analyze(self, symbol: str, articles: List[dict], context: str) -> dict:
        if not self.model:
            return {
                "action": "HOLD",
                "severity": "LOW",
                "reasoning": "LLM not configured."
            }

        if not articles:
            return {
                "action": "HOLD",
                "severity": "LOW",
                "reasoning": "No news found."
            }

        # Prepare headlines for batch processing
        headlines_text = "\n".join([f"- [{a['source']}] {a['title']}" for a in articles[:5]])

        prompt = f"""
        Analyze these news headlines for stock '{symbol}' given the market context:
        
        Market Context: "{context}"
        
        Headlines:
        {headlines_text}

        Task:
        1. Identify the single most important news item from the list.
        2. Determine the trading action (BUY, SELL, HOLD) based on that item and the context.
        3. Assess severity (HIGH, MEDIUM, LOW).
        
        Return ONLY a JSON object in this format:
        {{
            "action": "BUY/SELL/HOLD",
            "severity": "HIGH/MEDIUM/LOW",
            "reasoning": "Reasoning based on [Source]: Headline...",
            "headline": "The specific headline used for analysis",
            "source": "The source of that headline"
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:-3]
            return json.loads(text)
        except Exception as e:
            print(f"LLM Error: {e}")
            return {
                "action": "HOLD",
                "severity": "LOW",
                "reasoning": "Failed to analyze with AI."
            }

from concurrent.futures import ThreadPoolExecutor, as_completed

class MarketAnalyzer:
    def __init__(self):
        self.fetcher = NewsFetcher()
        self.llm = LLMAnalyzer()
        self.market_data = MarketDataProvider()

    def process_stock(self, stock: Stock) -> Optional[Whisper]:
        try:
            print(f"Processing {stock.symbol}...")
            # Fetch market context
            context = self.market_data.get_context(stock.symbol)
            print(f"Context for {stock.symbol}: {context[:50]}...")
            
            # Fetch news
            articles = self.fetcher.fetch_news(stock.symbol)
            print(f"Found {len(articles)} articles for {stock.symbol}")
            
            if not articles:
                print(f"No articles for {stock.symbol}")
                return None

            # Batch analysis with LLM
            print(f"Analyzing {stock.symbol} with LLM...")
            analysis = self.llm.analyze(stock.symbol, articles, context)
            print(f"LLM Result for {stock.symbol}: {analysis}")
            
            # Create whisper
            # Relaxed filtering for debugging: Show everything except explicit failures
            if True: 
                w = Whisper(
                    symbol=stock.symbol,
                    type="NEWS",
                    severity=analysis.get('severity', 'LOW'),
                    message=f"[{analysis.get('source', 'Unknown')}] {analysis.get('headline', 'Market Update')}",
                    reasoning=analysis.get('reasoning', 'AI Analysis'),
                    action=analysis.get('action', 'HOLD')
                )
                print(f"Created whisper for {stock.symbol}: {w}")
                return w
        except Exception as e:
            print(f"Error processing {stock.symbol}: {e}")
            return None

    def analyze_stocks(self, stocks: List[Stock]) -> List[Whisper]:
        whispers = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_stock = {executor.submit(self.process_stock, stock): stock for stock in stocks}
            for future in as_completed(future_to_stock):
                whisper = future.result()
                if whisper:
                    whispers.append(whisper)
        return whispers
