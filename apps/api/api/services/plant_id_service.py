import httpx
import os
from typing import Dict, Any, Optional
from ..core.config import settings

class PlantIDService:
    """Service for plant identification using Plant.ID API"""

    BASE_URL = "https://api.plant.id/v2"
    API_KEY = settings.PLANT_ID_API_KEY

    @staticmethod
    async def identify_plant(image_data: str, plant_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Identify a plant using Plant.ID API

        Args:
            image_data: Base64 encoded image data
            plant_details: Additional plant details (location, etc.)

        Returns:
            Plant identification results
        """
        if not PlantIDService.API_KEY:
            # Return mock data if no API key
            return {
                "species": plant_details.get("species", "Unknown"),
                "confidence": 0.85,
                "common_names": ["Unknown Plant"],
                "description": "Plant identification service unavailable",
                "care_instructions": "General plant care: water when soil is dry, provide adequate sunlight"
            }

        headers = {
            "Api-Key": PlantIDService.API_KEY,
            "Content-Type": "application/json"
        }

        # Prepare Plant.ID API request
        data = {
            "images": [image_data],
            "modifiers": ["crops", "similar_images"],
            "plant_details": [plant_details]
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{PlantIDService.BASE_URL}/identify",
                    headers=headers,
                    json=data,
                    timeout=30.0
                )
                response.raise_for_status()

                result = response.json()

                # Extract relevant information
                suggestions = result.get("suggestions", [])
                if suggestions:
                    best_match = suggestions[0]
                    return {
                        "species": best_match.get("plant_name", "Unknown"),
                        "confidence": best_match.get("probability", 0.0),
                        "common_names": best_match.get("plant_details", {}).get("common_names", []),
                        "description": best_match.get("plant_details", {}).get("wiki_description", {}).get("value", ""),
                        "care_instructions": "Species-specific care information would be provided here"
                    }
                else:
                    return {
                        "species": "Unknown",
                        "confidence": 0.0,
                        "common_names": [],
                        "description": "Unable to identify plant",
                        "care_instructions": "Please consult a local nursery or extension service"
                    }

            except httpx.RequestError as e:
                print(f"Plant.ID API request error: {e}")
                return {
                    "species": plant_details.get("species", "Unknown"),
                    "confidence": 0.0,
                    "common_names": [],
                    "description": "Plant identification service temporarily unavailable",
                    "care_instructions": "Continue with general plant care practices"
                }
            except httpx.HTTPStatusError as e:
                print(f"Plant.ID API HTTP error: {e}")
                return {
                    "species": plant_details.get("species", "Unknown"),
                    "confidence": 0.0,
                    "common_names": [],
                    "description": "Plant identification service error",
                    "care_instructions": "Please try again later"
                }
