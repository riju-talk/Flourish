"""
Care-context routes: real-time external data (weather, botanical info) used to enrich
plant-care advice. These are plain REST endpoints - not a Model Context Protocol
server. The real MCP server is apps/api/mcp_server.py.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from ..services.weather_service import WeatherService
from ..services.groq_service import GroqService
from ..core.auth import verify_firebase_token
from ..core.rate_limit import lookup_limit

router = APIRouter()

@router.get("/weather/{lat}/{lon}")
async def get_weather_context(lat: float, lon: float, user_id: str = Depends(verify_firebase_token)):
    """Get real-time weather as plant-care context."""
    try:
        weather_data = await WeatherService.get_weather_by_location(lat, lon)
        return {
            "source": "OpenWeatherMap",
            "data": weather_data,
            "recommendation": "High humidity detected. Adjust watering for indoor tropicals." if weather_data.get("humidity", 0) > 70 else "Normal conditions."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/plant-info/{name}")
async def get_plant_info_context(name: str, user_id: str = Depends(lookup_limit)):
    """Fetch botanical/care data for a plant species."""
    try:
        plant_data = await GroqService.get_plant_info_agentic(name)
        return {
            "source": "Botanical database",
            "name": name,
            "details": plant_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
