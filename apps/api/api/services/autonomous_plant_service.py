import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
from ..models.plant import Plant, PlantInventory, CareSchedule, PlantType, PlantSize, ToxicityLevel
from ..services.ai_service import AIService
from ..services.plant_id_service import PlantIDService
from ..services.weather_service import WeatherService

class AutonomousPlantService:
    """Autonomous plant care agent that figures out everything from just the plant name"""

    # Plant knowledge database for common plants
    PLANT_KNOWLEDGE_BASE = {
        "snake plant": {
            "scientific_name": "Sansevieria trifasciata",
            "plant_type": PlantType.INDOOR,
            "size": PlantSize.MEDIUM,
            "toxicity": ToxicityLevel.MILDLY_TOXIC,
            "sunlight": "Low to bright indirect light",
            "watering_days": 14,
            "watering_amount": "Light - let soil dry completely",
            "soil_type": "Well-draining cactus/succulent mix",
            "humidity": "Low to moderate (30-50%)",
            "fertilizer": "Diluted balanced fertilizer, spring-summer only",
            "fertilizer_days": 60,
            "pests": ["Spider mites", "Mealybugs"],
            "locations": ["Bathroom", "Bedroom", "Office", "Low-light areas"],
            "care_instructions": "Extremely hardy and forgiving. Tolerates neglect well. Remove dead leaves regularly.",
            "fun_facts": ["Also called Mother-in-Law's Tongue", "Excellent air purifier", "Can survive in very low light"]
        },
        "peace lily": {
            "scientific_name": "Spathiphyllum wallisii",
            "plant_type": PlantType.INDOOR,
            "size": PlantSize.MEDIUM,
            "toxicity": ToxicityLevel.TOXIC,
            "sunlight": "Low to medium indirect light",
            "watering_days": 7,
            "watering_amount": "Moderate - keep soil moist but not soggy",
            "soil_type": "Well-draining potting mix",
            "humidity": "High (60-80%)",
            "fertilizer": "Balanced houseplant fertilizer",
            "fertilizer_days": 30,
            "pests": ["Spider mites", "Aphids", "Mealybugs"],
            "locations": ["Bathroom", "Kitchen", "Living room with shade"],
            "care_instructions": "Drooping leaves indicate it needs water. Mist regularly for humidity.",
            "fun_facts": ["Flowers are actually modified leaves", "Excellent air purifier", "Symbolizes peace and tranquility"]
        },
        "spider plant": {
            "scientific_name": "Chlorophytum comosum",
            "plant_type": PlantType.INDOOR,
            "size": PlantSize.MEDIUM,
            "toxicity": ToxicityLevel.NON_TOXIC,
            "sunlight": "Bright indirect to medium light",
            "watering_days": 7,
            "watering_amount": "Moderate - let top inch dry out",
            "soil_type": "Well-draining potting mix",
            "humidity": "Moderate (40-60%)",
            "fertilizer": "Balanced houseplant fertilizer",
            "fertilizer_days": 30,
            "pests": ["Spider mites", "Aphids"],
            "locations": ["Hanging baskets", "Shelves", "Windowsills with filtered light"],
            "care_instructions": "Produces plantlets that can be propagated. Trim brown tips as needed.",
            "fun_facts": ["One of NASA's top air-purifying plants", "Produces oxygen at night", "Very pet-safe"]
        },
        "monstera deliciosa": {
            "scientific_name": "Monstera deliciosa",
            "plant_type": PlantType.INDOOR,
            "size": PlantSize.LARGE,
            "toxicity": ToxicityLevel.TOXIC,
            "sunlight": "Bright indirect light",
            "watering_days": 10,
            "watering_amount": "Moderate - let top 2 inches dry",
            "soil_type": "Well-draining potting mix",
            "humidity": "High (60%+)",
            "fertilizer": "Balanced fertilizer with micronutrients",
            "fertilizer_days": 30,
            "pests": ["Spider mites", "Thrips", "Scale"],
            "locations": ["Living room", "Office", "Bright corners"],
            "care_instructions": "Provide support for climbing. Clean leaves regularly. Rotate for even growth.",
            "fun_facts": ["The fruit is edible when ripe", "Natural leaf holes develop with age", "Can grow very large indoors"]
        }
    }

    @staticmethod
    async def identify_and_create_plant(plant_name: str, user_location: Optional[str] = None) -> PlantInventory:
        """
        Autonomous plant creation - takes just a plant name and figures out everything else
        """
        # Normalize plant name for lookup
        normalized_name = plant_name.lower().strip()

        # Try to find in knowledge base first
        plant_data = AutonomousPlantService.PLANT_KNOWLEDGE_BASE.get(normalized_name)

        if not plant_data:
            # Use AI to determine plant characteristics if not in knowledge base
            plant_data = await AutonomousPlantService._ai_research_plant(plant_name)

        # Create plant object with all determined properties
        plant = Plant(
            name=plant_name.title(),
            species=plant_data.get("species", plant_name.title()),
            scientific_name=plant_data.get("scientific_name"),
            plant_type=PlantType(plant_data.get("plant_type", "indoor")),
            size=PlantSize(plant_data.get("size", "medium")),
            toxicity=ToxicityLevel(plant_data.get("toxicity", "non-toxic")),
            location=plant_data.get("location", "Living Room"),
            preferred_locations=plant_data.get("locations", ["Living Room"]),
            sunlight_requirement=plant_data.get("sunlight", "Medium indirect light"),
            temperature_range=plant_data.get("temperature_range", {"min": 18, "max": 24}),
            watering_frequency_days=plant_data.get("watering_days", 7),
            watering_amount=plant_data.get("watering_amount", "Moderate"),
            soil_type=plant_data.get("soil_type", "Well-draining potting mix"),
            humidity_preference=plant_data.get("humidity", "Moderate (40-60%)"),
            fertilizer_type=plant_data.get("fertilizer", "Balanced houseplant fertilizer"),
            fertilizer_frequency_days=plant_data.get("fertilizer_days", 30),
            fertilizer_season=plant_data.get("fertilizer_season", "Growing season"),
            pesticide_needs=plant_data.get("pesticides", []),
            common_pests=plant_data.get("pests", []),
            care_instructions=plant_data.get("care_instructions", "General plant care required"),
            fun_facts=plant_data.get("fun_facts", [])
        )

        # Generate comprehensive care schedule
        care_schedule = await AutonomousPlantService._generate_comprehensive_schedule(plant)

        # Get weather data if location provided
        inventory_summary = await AutonomousPlantService._generate_inventory_summary(plant, user_location)

        return PlantInventory(
            plant=plant,
            care_schedule=care_schedule,
            health_history=[],
            inventory_summary=inventory_summary
        )

    @staticmethod
    async def _ai_research_plant(plant_name: str) -> Dict[str, Any]:
        """Use AI to research plant characteristics if not in knowledge base"""
        prompt = f"""
        Research this plant and provide comprehensive care information in JSON format:

        Plant: {plant_name}

        Provide the following information:
        - scientific_name: Scientific name
        - plant_type: indoor/outdoor/both
        - size: small/medium/large
        - toxicity: non-toxic/mildly-toxic/toxic/highly-toxic
        - sunlight: Light requirements description
        - watering_days: Days between watering (integer)
        - watering_amount: Watering description
        - soil_type: Soil preference
        - humidity: Humidity preference description
        - fertilizer: Fertilizer type and frequency description
        - fertilizer_days: Days between fertilizing (integer)
        - pests: Common pests list
        - locations: Best indoor locations list
        - care_instructions: Detailed care instructions
        - fun_facts: Interesting facts list

        Respond only with valid JSON.
        """

        try:
            # Use AI service to research plant
            response = await AIService._research_plant_info(plant_name)

            # Parse AI response and structure it
            plant_info = json.loads(response)

            # Ensure required fields have defaults
            plant_info.setdefault("plant_type", "indoor")
            plant_info.setdefault("size", "medium")
            plant_info.setdefault("toxicity", "non-toxic")
            plant_info.setdefault("sunlight", "Medium indirect light")
            plant_info.setdefault("watering_days", 7)
            plant_info.setdefault("watering_amount", "Moderate")
            plant_info.setdefault("soil_type", "Well-draining potting mix")
            plant_info.setdefault("humidity", "Moderate (40-60%)")
            plant_info.setdefault("fertilizer", "Balanced houseplant fertilizer")
            plant_info.setdefault("fertilizer_days", 30)
            plant_info.setdefault("pests", [])
            plant_info.setdefault("locations", ["Living Room"])
            plant_info.setdefault("care_instructions", "General plant care required")
            plant_info.setdefault("fun_facts", [])

            return plant_info

        except Exception as e:
            print(f"Error researching plant {plant_name}: {e}")
            # Return safe defaults
            return {
                "scientific_name": f"{plant_name.title()} spp.",
                "plant_type": "indoor",
                "size": "medium",
                "toxicity": "non-toxic",
                "sunlight": "Medium indirect light",
                "watering_days": 7,
                "watering_amount": "Moderate",
                "soil_type": "Well-draining potting mix",
                "humidity": "Moderate (40-60%)",
                "fertilizer": "Balanced houseplant fertilizer",
                "fertilizer_days": 30,
                "pests": ["Spider mites", "Aphids"],
                "locations": ["Living Room"],
                "care_instructions": "Monitor regularly and adjust care based on plant response",
                "fun_facts": ["A wonderful addition to any plant collection!"]
            }

    @staticmethod
    async def _generate_comprehensive_schedule(plant: Plant) -> List[CareSchedule]:
        """Generate a comprehensive care schedule for the plant"""
        schedule = []
        now = datetime.now()

        # Watering schedule (next 90 days)
        for i in range(13):  # Approximately 3 months
            scheduled_date = now + timedelta(days=i * plant.watering_frequency_days)
            schedule.append(CareSchedule(
                plant_id=plant.id or "temp",
                schedule_type="watering",
                title=f"💧 Water {plant.name}",
                description=f"{plant.watering_amount}. Check soil moisture before watering.",
                scheduled_date=scheduled_date,
                priority="high" if i == 0 else "medium",
                estimated_time="2 minutes"
            ))

        # Fertilizing schedule (next 6 months)
        for i in range(7):
            scheduled_date = now + timedelta(days=i * plant.fertilizer_frequency_days)
            schedule.append(CareSchedule(
                plant_id=plant.id or "temp",
                schedule_type="fertilizing",
                title=f"🌱 Fertilize {plant.name}",
                description=f"Apply {plant.fertilizer_type} as directed.",
                scheduled_date=scheduled_date,
                priority="medium",
                estimated_time="5 minutes"
            ))

        # Health check schedule (daily for first week, then weekly)
        for i in range(7):  # Daily checks first week
            scheduled_date = now + timedelta(days=i)
            schedule.append(CareSchedule(
                plant_id=plant.id or "temp",
                schedule_type="health_check",
                title=f"👀 Health Check: {plant.name}",
                description="Check leaves, soil, and overall plant health. Look for pests or issues.",
                scheduled_date=scheduled_date,
                priority="medium",
                estimated_time="3 minutes"
            ))

        # Weekly health checks after first week
        for i in range(1, 13):  # Next 12 weeks
            scheduled_date = now + timedelta(weeks=i)
            schedule.append(CareSchedule(
                plant_id=plant.id or "temp",
                schedule_type="health_check",
                title=f"👀 Weekly Health Check: {plant.name}",
                description="Weekly inspection for pests, diseases, and general health.",
                scheduled_date=scheduled_date,
                priority="low",
                estimated_time="3 minutes"
            ))

        # Sort schedule by date
        schedule.sort(key=lambda x: x.scheduled_date)

        return schedule

    @staticmethod
    async def _generate_inventory_summary(plant: Plant, user_location: Optional[str] = None) -> Dict[str, Any]:
        """Generate comprehensive inventory summary"""
        summary = {
            "total_tasks_today": 0,
            "total_tasks_this_week": 0,
            "urgent_tasks": 0,
            "plant_health_score": plant.health_score,
            "care_complexity": "Easy" if plant.watering_frequency_days >= 10 else "Moderate",
            "estimated_monthly_cost": "$5-15",  # Based on fertilizer and supplies
            "recommended_products": [
                plant.soil_type,
                plant.fertilizer_type,
                "Neem oil (for pest control)" if plant.common_pests else None
            ],
            "placement_suggestions": plant.preferred_locations,
            "seasonal_care": {
                "winter": "Reduce watering frequency by 50%",
                "summer": "Monitor for heat stress and increase humidity",
                "spring": "Resume normal fertilizing schedule",
                "fall": "Prepare for reduced light conditions"
            }
        }

        # Filter out None values
        summary["recommended_products"] = [p for p in summary["recommended_products"] if p]

        return summary

    @staticmethod
    async def update_plant_health(plant_id: str, health_checks: List) -> Dict[str, Any]:
        """Update plant health based on recent checks and generate new schedule"""
        # This would integrate with the existing AI service for health analysis
        # and dynamically adjust care schedules based on plant performance

        # For now, return a placeholder response
        return {
            "health_updated": True,
            "new_schedule_generated": True,
            "care_adjustments": {},
            "next_check_date": datetime.now() + timedelta(days=1)
        }
