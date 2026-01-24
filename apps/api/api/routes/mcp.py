from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from ..services.weather_service import WeatherService
from ..services.plant_id_service import PlantIDService
from ..core.auth import verify_firebase_token

router = APIRouter()

@router.get("/weather/{lat}/{lon}")
async def get_mcp_weather(lat: float, lon: float, user_id: str = Depends(verify_firebase_token)):
    """MCP Tool: Get real-time weather for plant care context"""
    try:
        weather_data = await WeatherService.get_weather(lat, lon)
        return {
            "source": "OpenWeatherMap via Flourish MCP",
            "data": weather_data,
            "recommendation": "High humidity detected. Adjust watering for indoor tropicals." if weather_data.get("humidity", 0) > 70 else "Normal conditions."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/plant-info/{name}")
async def get_mcp_plant_info(name: str, user_id: str = Depends(verify_firebase_token)):
    """MCP Tool: Fetch botanical data for a plant species"""
    try:
        # This would interface with PlantIDService or Trefle
        plant_data = await PlantIDService.get_plant_details(name)
        return {
            "source": "Botanical Database via Flourish MCP",
            "name": name,
            "details": plant_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
