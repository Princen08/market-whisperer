import feedparser
from textblob import TextBlob
from typing import List
import urllib.parse
from .models import Whisper, Stock

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

    def analyze(self, symbol: str, title: str, source: str) -> dict:
        if not self.model:
            # Fallback if no API key
            return {
                "action": "HOLD",
                "severity": "LOW",
                "reasoning": "LLM not configured. Please set GEMINI_API_KEY."
            }

        prompt = f"""
        Analyze this news headline for stock '{symbol}':
        Headline: "{title}"
        Source: "{source}"

        Determine the trading action (BUY, SELL, HOLD), severity (HIGH, MEDIUM, LOW), and provide a short reasoning (max 1 sentence).
        Return ONLY a JSON object in this format:
        {{
            "action": "BUY/SELL/HOLD",
            "severity": "HIGH/MEDIUM/LOW",
            "reasoning": "Your reasoning here."
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Clean up response to ensure valid JSON
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

class MarketAnalyzer:
    def __init__(self):
        self.fetcher = NewsFetcher()
        self.llm = LLMAnalyzer()

    def analyze_stocks(self, stocks: List[Stock]) -> List[Whisper]:
        whispers = []
        for stock in stocks:
            articles = self.fetcher.fetch_news(stock.symbol)
            
            for article in articles:
                title = article['title']
                source = article['source']
                
                # Use LLM for analysis
                analysis = self.llm.analyze(stock.symbol, title, source)
                
                # Create whisper
                # Relaxed filtering for debugging: Show everything except explicit failures
                if True: 
                    whispers.append(Whisper(
                        symbol=stock.symbol,
                        type="NEWS", # Simplified type for now
                        severity=analysis.get('severity', 'LOW'),
                        message=f"[{source}] {title}",
                        reasoning=analysis.get('reasoning', 'AI Analysis'),
                        action=analysis.get('action', 'HOLD')
                    ))
                    
                    # Limit to 1 whisper per stock
                    break 
                    
        return whispers
