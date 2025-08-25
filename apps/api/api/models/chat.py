from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    image_url: Optional[str] = None
    timestamp: datetime = datetime.now()

class ChatResponse(BaseModel):
    response: str
    suggestions: List[str] = []
    timestamp: datetime = datetime.now()

class ImageAnalysis(BaseModel):
    health_assessment: str
    issues_detected: List[str] = []
    recommendations: List[str] = []
    confidence: float = 0.0