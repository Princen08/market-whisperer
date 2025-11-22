from pydantic import BaseModel
from typing import List, Optional

class Stock(BaseModel):
    symbol: str
    name: Optional[str] = None

class Whisper(BaseModel):
    symbol: str
    type: str  # "NEWS", "MOVEMENT", "MERGER"
    severity: str # "HIGH", "MEDIUM", "LOW"
    message: str
    reasoning: str # Explanation for the action
    action: str # "BUY", "SELL", "HOLD"

class AnalysisResult(BaseModel):
    whispers: List[Whisper]
