from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from ..models.chat import ChatMessage, ChatResponse, ImageAnalysis
from ..services.ai_service import AIService
from ..services.weather_service import WeatherService
from ..core.auth import verify_firebase_token

router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def chat_with_ai(
    messages: List[ChatMessage],
    user_id: str = Depends(verify_firebase_token)
):
    """Enhanced multi-modal chat with PlantMind AI"""
    try:
        # Extract location from messages if provided for weather integration
        context = {}
        for msg in messages:
            if "location" in msg.content.lower() or "weather" in msg.content.lower():
                # In a real app, you'd extract coordinates from user location
                # For now, we'll use default weather data
                context["weather_requested"] = True

        response = await AIService.chat_with_ai(messages, context)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-image", response_model=ImageAnalysis)
async def analyze_plant_image(
    image_data: Dict[str, Any],
    user_id: str = Depends(verify_firebase_token)
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
    user_id: str = Depends(verify_firebase_token)
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