from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from ..models.chat import (
    ChatMessage, ChatResponse, ImageAnalysis, ChatSessionSummary, ChatSessionDetail,
    SessionMessage, CreateSessionRequest, RenameSessionRequest, SendMessageRequest,
    SendMessageResponse,
)
from ..db.firestore import FirestoreDB
from ..services.ai_service import AIService
from ..services.groq_service import GroqService
from ..services.weather_service import WeatherService
from ..services.plant_service import PlantService
from ..core.auth import verify_firebase_token
from ..core.rate_limit import chat_limit, vision_limit

router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def chat_with_ai(
    messages: List[ChatMessage],
    context: Optional[str] = None,
    user_id: str = Depends(chat_limit)
):
    """
    Agentic multi-modal chat via Groq (PlantMind)
    Supports context-aware plant care conversations, grounded in the user's own garden
    """
    try:
        response = await GroqService.chat_with_ai(messages, user_id=user_id, context=context)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============ Persistent chat sessions (ChatGPT-style) ============
# The stateless POST "/" above is kept for the embedded assistant widgets; the full-page
# chat uses these endpoints so conversations survive a refresh and show up in the
# sidebar. History is loaded server-side, so the client only ever sends the new message.

HISTORY_WINDOW = 20      # most recent messages given to the model as context
MAX_MESSAGE_CHARS = 4000


def _summary(session: dict) -> ChatSessionSummary:
    return ChatSessionSummary(
        id=session["id"],
        title=session.get("title") or "New chat",
        created_at=session.get("created_at"),
        updated_at=session.get("updated_at"),
        message_count=session.get("message_count", 0),
    )


def _message(m: dict) -> SessionMessage:
    return SessionMessage(
        id=m["id"], role=m["role"], content=m["content"],
        suggestions=m.get("suggestions") or [], created_at=m.get("created_at"),
    )


async def _owned_session(session_id: str, user_id: str) -> dict:
    session = await FirestoreDB.get_chat_session(session_id, user_id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat not found")
    return session


@router.get("/sessions", response_model=List[ChatSessionSummary])
async def list_sessions(user_id: str = Depends(verify_firebase_token)):
    sessions = await FirestoreDB.list_chat_sessions(user_id)
    return [_summary(s) for s in sessions]


@router.post("/sessions", response_model=ChatSessionSummary)
async def create_session(
    body: CreateSessionRequest = CreateSessionRequest(),
    user_id: str = Depends(verify_firebase_token),
):
    return _summary(await FirestoreDB.create_chat_session(user_id, body.title))


@router.get("/sessions/{session_id}", response_model=ChatSessionDetail)
async def get_session(session_id: str, user_id: str = Depends(verify_firebase_token)):
    session = await _owned_session(session_id, user_id)
    messages = await FirestoreDB.get_chat_messages(session_id)
    return ChatSessionDetail(**_summary(session).model_dump(), messages=[_message(m) for m in messages])


@router.patch("/sessions/{session_id}", response_model=ChatSessionSummary)
async def rename_session(
    session_id: str, body: RenameSessionRequest, user_id: str = Depends(verify_firebase_token)
):
    session = await _owned_session(session_id, user_id)
    title = " ".join(body.title.split())[:80]
    if not title:
        raise HTTPException(status_code=422, detail="Title cannot be empty")
    # title_locked stops auto-titling from overwriting a name the user chose.
    await FirestoreDB.update_chat_session(session_id, {"title": title, "title_locked": True})
    return _summary({**session, "title": title})


@router.delete("/sessions/{session_id}", status_code=204)
async def delete_session(session_id: str, user_id: str = Depends(verify_firebase_token)):
    await _owned_session(session_id, user_id)
    await FirestoreDB.delete_chat_session(session_id)


@router.post("/sessions/{session_id}/messages", response_model=SendMessageResponse)
async def send_session_message(
    session_id: str, body: SendMessageRequest, user_id: str = Depends(chat_limit)
):
    session = await _owned_session(session_id, user_id)
    content = body.content.strip()
    if not content:
        raise HTTPException(status_code=422, detail="Message cannot be empty")
    if len(content) > MAX_MESSAGE_CHARS:
        raise HTTPException(status_code=422, detail=f"Message exceeds {MAX_MESSAGE_CHARS} characters")

    history = await FirestoreDB.get_chat_messages(session_id, limit=HISTORY_WINDOW)
    turns = [ChatMessage(role=m["role"], content=m["content"]) for m in history]
    turns.append(ChatMessage(role="user", content=content))

    reply = await GroqService.chat_with_ai(turns, user_id=user_id, context=body.context)

    if reply.error:
        # Nothing is saved for a failed turn - the client shows the notice and lets the
        # user retry, so history never contains "trouble reaching PlantMind" replies.
        return SendMessageResponse(
            session=_summary(session),
            assistant_message=SessionMessage(id="error", role="assistant",
                                             content=reply.response, suggestions=reply.suggestions),
            error=True,
        )

    user_msg = await FirestoreDB.add_chat_message(session_id, "user", content)
    assistant_msg = await FirestoreDB.add_chat_message(
        session_id, "assistant", reply.response, reply.suggestions
    )

    updates = {"updated_at": assistant_msg["created_at"],
               "message_count": session.get("message_count", 0) + 2}
    if session.get("message_count", 0) == 0 and not session.get("title_locked"):
        updates["title"] = await GroqService.generate_chat_title(content)
    await FirestoreDB.update_chat_session(session_id, updates)

    return SendMessageResponse(
        session=_summary({**session, **updates}),
        user_message=_message(user_msg),
        assistant_message=_message(assistant_msg),
    )


@router.post("/analyze-image", response_model=ImageAnalysis)
async def analyze_plant_image(
    image_data: Dict[str, Any],
    user_id: str = Depends(vision_limit)
):
    """Enhanced plant image analysis with external APIs"""
    try:
        # Extract base64 image data
        image_base64 = image_data.get("image_data")
        if not image_base64:
            raise HTTPException(status_code=400, detail="Image data required")

        analysis = await AIService.analyze_plant_image(image_base64)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/weather/{lat}/{lon}")
async def get_weather_data(
    lat: float,
    lon: float,
    user_id: str = Depends(verify_firebase_token)
):
    """Get weather data for plant care recommendations"""
    try:
        weather_data = await WeatherService.get_weather_by_location(lat, lon)
        return weather_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/care-plan")
async def generate_care_plan(
    plant_data: Dict[str, Any],
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    user_id: str = Depends(vision_limit)
):
    """Generate structured care plan for a plant"""
    try:
        # Get weather data if location provided
        weather_data = None
        if lat and lon:
            weather_data = await WeatherService.get_weather_by_location(lat, lon)

        # Mock plant object for AI service
        from ..models.plant import Plant
        plant = Plant(
            id="temp",
            name=plant_data.get("name", "Unknown"),
            species=plant_data.get("species", "Unknown"),
            location=plant_data.get("location", "Unknown"),
            sunlight_requirement=plant_data.get("sunlight", "Medium"),
            health_status="Good"
        )

        care_plan = await AIService.generate_care_plan(plant, weather_data)

        return {
            "care_plan": care_plan,
            "weather_considerations": weather_data is not None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))