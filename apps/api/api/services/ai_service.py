import os
import json
from typing import List, Dict, Any
from groq import Groq
from ..models.plant import Plant, HealthCheckItem, PlantAnalysis
from ..models.chat import ChatMessage, ChatResponse, ImageAnalysis

# Initialize Groq client
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# System prompt for plant care assistant
PLANT_AI_SYSTEM_PROMPT = """You are PlantMind, an advanced AI plant care agent. You are proactive, knowledgeable, and caring about plant health. Your responsibilities include:

1. PROACTIVE MONITORING: Analyze daily health check data and predict issues before they become serious
2. SMART SCHEDULING: Generate optimal care schedules based on plant species, environment, and health status
3. HEALTH ANALYSIS: Evaluate plant health from images and user reports, providing actionable insights
4. PERSONALIZED ADVICE: Give specific, actionable advice tailored to each plant and user's situation
5. PREVENTIVE CARE: Suggest preventive measures to maintain optimal plant health

When analyzing plant health:
- Consider species-specific needs
- Factor in environmental conditions
- Look for early warning signs
- Provide specific, actionable recommendations
- Suggest optimal timing for interventions

Be encouraging, informative, and always focus on helping plants thrive."""

class AIService:
    @staticmethod
    async def analyze_plant_health(plant: Plant, health_checks: List[HealthCheckItem]) -> PlantAnalysis:
        """AI-powered plant health analysis"""
        
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
        
        for check in health_checks[-5:]:  # Last 5 checks
            context += f"- {check.check_type}: {check.status} ({check.notes or 'No notes'})\n"
        
        prompt = f"""
        {PLANT_AI_SYSTEM_PROMPT}
        
        Analyze this plant's health and provide:
        1. Health score (0-100)
        2. Current issues (if any)
        3. Specific recommendations
        4. Next actions to take
        
        Plant data:
        {context}
        
        Respond in JSON format:
        {{
            "health_score": float,
            "issues": [list of current issues],
            "recommendations": [list of specific recommendations],
            "next_actions": [list of immediate actions needed]
        }}
        """
        
        try:
            response = groq_client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            analysis_data = json.loads(response.choices[0].message.content)
            
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
        """Multi-modal chat with PlantMind AI"""
        try:
            # Prepare messages for Groq
            groq_messages = [{"role": "system", "content": PLANT_AI_SYSTEM_PROMPT}]
            
            for msg in messages:
                groq_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
            
            response = groq_client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=groq_messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            ai_response = response.choices[0].message.content
            
            return ChatResponse(
                response=ai_response,
                suggestions=[
                    "Tell me about my plant's health",
                    "What should I do today?",
                    "Help me identify this plant issue"
                ]
            )
        except Exception as e:
            print(f"Error in AI chat: {e}")
            return ChatResponse(
                response="I'm having trouble processing your request right now. Please try again.",
                suggestions=["Try asking about plant care basics"]
            )

    @staticmethod
    async def analyze_plant_image(image_data: str) -> ImageAnalysis:
        """Analyze plant image for health assessment"""
        try:
            # In a real implementation, you'd use a vision model here
            # For now, return mock analysis
            return ImageAnalysis(
                health_assessment="Plant appears healthy with vibrant green leaves",
                issues_detected=[],
                recommendations=[
                    "Continue current care routine",
                    "Monitor for any changes in leaf color"
                ],
                confidence=0.85
            )
        except Exception as e:
            print(f"Error in image analysis: {e}")
            return ImageAnalysis(
                health_assessment="Unable to analyze image",
                issues_detected=["Image analysis failed"],
                recommendations=["Please try uploading a clearer image"],
                confidence=0.0
            )