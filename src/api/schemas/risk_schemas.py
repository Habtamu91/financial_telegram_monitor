from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class RiskScoreRequest(BaseModel):
    message_text: str
    channel: Optional[str] = None
    authorized: bool = True

class MessageAnalysis(BaseModel):
    id: int
    text: str
    channel: str
    date: datetime
    risk_score: float
    detected_products: List[str]
    risk_factors: List[str]

class RiskScoreResponse(BaseModel):
    risk_score: float
    risk_level: str  # "LOW", "MEDIUM", "HIGH"
    detected_products: List[str]
    risk_factors: List[str]
    confidence: float



