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
    # True when GroqService returned its fallback message instead of a real answer
    # (missing key, provider outage, tool failure). Persisted chat sessions skip saving
    # such turns so history never fills up with "trouble reaching PlantMind" replies.
    error: bool = False


class SessionMessage(BaseModel):
    id: str
    role: str
    content: str
    suggestions: List[str] = []
    created_at: Optional[datetime] = None


class ChatSessionSummary(BaseModel):
    id: str
    title: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    message_count: int = 0


class ChatSessionDetail(ChatSessionSummary):
    messages: List[SessionMessage] = []


class CreateSessionRequest(BaseModel):
    title: Optional[str] = None


class RenameSessionRequest(BaseModel):
    title: str


class SendMessageRequest(BaseModel):
    content: str
    context: Optional[str] = None


class SendMessageResponse(BaseModel):
    session: ChatSessionSummary
    user_message: Optional[SessionMessage] = None
    assistant_message: SessionMessage
    error: bool = False

class ImageAnalysis(BaseModel):
    health_assessment: str
    issues_detected: List[str] = []
    recommendations: List[str] = []
    confidence: float = 0.0