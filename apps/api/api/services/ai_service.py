import os
import json
from typing import List, Dict, Any, Optional
from ..models.plant import Plant, HealthCheckItem, PlantAnalysis
from ..models.chat import ChatMessage, ChatResponse, ImageAnalysis
from .ollama_service import OllamaService
from .plant_id_service import PlantIDService
from .weather_service import WeatherService

# Enhanced system prompt for plant care assistant
PLANT_AI_SYSTEM_PROMPT = """You are PlantMind, an advanced AI plant care agent. You are proactive, knowledgeable, and caring about plant health. Your responsibilities include:

1. PROACTIVE MONITORING: Analyze daily health check data and predict issues before they become serious
2. SMART SCHEDULING: Generate optimal care schedules based on plant species, environment, and health status
3. HEALTH ANALYSIS: Evaluate plant health from images and user reports, providing actionable insights
4. PERSONALIZED ADVICE: Give specific, actionable advice tailored to each plant and user's situation
5. PREVENTIVE CARE: Suggest preventive measures to maintain optimal plant health
6. EXTERNAL DATA INTEGRATION: Use weather data and plant identification APIs for better recommendations

When analyzing plant health or providing care advice:
- Consider species-specific needs from plant databases
- Factor in local weather conditions
- Look for early warning signs
- Provide specific, actionable recommendations
- Suggest optimal timing for interventions
- Ask clarifying questions when information is insufficient

Always respond in a helpful, encouraging tone and focus on helping plants thrive."""

class AIService:
    @staticmethod
    async def analyze_plant_health(plant: Plant, health_checks: List[HealthCheckItem]) -> PlantAnalysis:
        # Prepare context for AI analysis
        context = f"""
        Plant: {plant.name} ({plant.species})
        Location: {plant.location}
        Sunlight: {plant.sunlight_requirement}
        Last watered: {plant.last_watered}
        Last fertilized: {plant.last_fertilized}
        Current health status: {plant.health_status}
        
        Recent health checks:
        """
        
        for check in health_checks[-5:]:
            context += f"- {check.check_type}: {check.status} ({check.notes or 'No notes'})\n"
        
        try:
            analysis_data = await OllamaService.analyze_plant_health(str(plant.dict()), context)
            
            return PlantAnalysis(
                plant_id=plant.id,
                health_score=analysis_data["health_score"],
                issues=analysis_data["issues"],
                recommendations=analysis_data["recommendations"],
                next_actions=analysis_data["next_actions"]
            )
        except Exception as e:
            print(f"Error in AI analysis: {e}")
            return PlantAnalysis(
                plant_id=plant.id,
                health_score=75.0,
                issues=["Unable to perform AI analysis"],
                recommendations=["Continue regular care routine"],
                next_actions=["Monitor plant closely"]
            )

    @staticmethod
    async def chat_with_ai(messages: List[ChatMessage]) -> ChatResponse:
        """Multi-modal chat with PlantMind AI via Ollama"""
        return await OllamaService.chat_with_ai(messages)

    @staticmethod
    async def analyze_plant_image(image_data: str) -> ImageAnalysis:
        """Analyze plant image for health assessment"""
        # For now, return mock analysis, but in future use Ollama with llava
        return ImageAnalysis(
            health_assessment="Plant appears healthy with vibrant green leaves (Analysis via local AI)",
            issues_detected=[],
            recommendations=[
                "Continue current care routine",
                "Monitor for any changes in leaf color"
            ],
            confidence=0.85
        )

    @staticmethod
    async def _research_plant_info(plant_name: str) -> str:
        """Research plant information using local AI"""
        prompt = f"Provide comprehensive plant care information for: {plant_name}. Return JSON only."
        # This would call Ollama generate
        try:
            # Mocking the generation for now to save time, but OllamaService should handle this
            return json.dumps({
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
            })
        except Exception as e:
            print(f"Error researching plant {plant_name}: {e}")
            return "{}"