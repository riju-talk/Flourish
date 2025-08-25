from fastapi import APIRouter, HTTPException
from typing import List
from ..models.chat import ChatMessage, ChatResponse, ImageAnalysis
from ..services.ai_service import AIService

router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def chat_with_ai(messages: List[ChatMessage]):
    """Multi-modal chat with PlantMind AI"""
    try:
        response = await AIService.chat_with_ai(messages)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-image", response_model=ImageAnalysis)
async def analyze_plant_image(image_data: str):
    """Analyze plant image for health assessment"""
    try:
        analysis = await AIService.analyze_plant_image(image_data)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))