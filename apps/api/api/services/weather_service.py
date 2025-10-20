import httpx
import os
from typing import Dict, Any, Optional
from ..core.config import settings

class WeatherService:
    """Service for weather data using OpenWeatherMap API"""

    BASE_URL = "http://api.openweathermap.org/data/2.5"
    API_KEY = settings.OPENWEATHER_API_KEY

    @staticmethod
    async def get_weather_by_location(lat: float, lon: float) -> Dict[str, Any]:
        """
        Get current weather data for a location

        Args:
            lat: Latitude
            lon: Longitude

        Returns:
            Weather data for plant care decisions
        """
        if not WeatherService.API_KEY:
            # Return mock data if no API key
            return {
                "temperature": 22.0,
                "humidity": 65.0,
                "condition": "Partly Cloudy",
                "wind_speed": 5.2,
                "recommendations": ["Moderate watering needed", "Good growing conditions"]
            }

        params = {
            "lat": lat,
            "lon": lon,
            "appid": WeatherService.API_KEY,
            "units": "metric"
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{WeatherService.BASE_URL}/weather",
                    params=params,
                    timeout=10.0
                )
                response.raise_for_status()

                data = response.json()

                # Extract plant-relevant weather data
                temp = data["main"]["temp"]
                humidity = data["main"]["humidity"]
                condition = data["weather"][0]["main"]

                # Generate plant care recommendations based on weather
                recommendations = WeatherService._generate_plant_recommendations(temp, humidity, condition)

                return {
                    "temperature": temp,
                    "humidity": humidity,
                    "condition": condition,
                    "wind_speed": data.get("wind", {}).get("speed", 0),
                    "recommendations": recommendations
                }

            except httpx.RequestError as e:
                print(f"OpenWeatherMap API request error: {e}")
                return {
                    "temperature": 20.0,
                    "humidity": 60.0,
                    "condition": "Unknown",
                    "wind_speed": 0.0,
                    "recommendations": ["Weather data unavailable", "Use general care guidelines"]
                }
            except httpx.HTTPStatusError as e:
                print(f"OpenWeatherMap API HTTP error: {e}")
                return {
                    "temperature": 20.0,
                    "humidity": 60.0,
                    "condition": "Unknown",
                    "wind_speed": 0.0,
                    "recommendations": ["Weather service error", "Please try again later"]
                }

    @staticmethod
    def _generate_plant_recommendations(temp: float, humidity: float, condition: str) -> list:
        """Generate plant care recommendations based on weather conditions"""
        recommendations = []

        # Temperature-based recommendations
        if temp > 30:
            recommendations.append("High temperature: Increase watering frequency")
            recommendations.append("Provide shade during peak heat hours")
        elif temp < 10:
            recommendations.append("Low temperature: Reduce watering and protect from frost")
        elif 15 <= temp <= 25:
            recommendations.append("Optimal temperature range for most plants")

        # Humidity-based recommendations
        if humidity < 40:
            recommendations.append("Low humidity: Consider misting plants regularly")
        elif humidity > 80:
            recommendations.append("High humidity: Ensure good air circulation to prevent mold")

        # Condition-based recommendations
        if "rain" in condition.lower():
            recommendations.append("Rain expected: Reduce manual watering")
        elif "clear" in condition.lower() or "sunny" in condition.lower():
            recommendations.append("Sunny conditions: Monitor soil moisture closely")

        if not recommendations:
            recommendations.append("Weather conditions appear normal")

        return recommendations
