import ollama
import json
from typing import List, Dict, Any, Optional
from ..models.plant import Plant, HealthCheckItem, PlantAnalysis
from ..models.chat import ChatMessage, ChatResponse

class OllamaService:
    MODEL = "llama3" # Default model

    @staticmethod
    async def chat_with_ai(messages: List[ChatMessage]) -> ChatResponse:
        try:
            ollama_messages = [{"role": m.role, "content": m.content} for m in messages]
            
            response = ollama.chat(
                model=OllamaService.MODEL,
                messages=ollama_messages,
            )
            
            content = response['message']['content']
            
            # Simple follow-up generation logic
            suggestions = [
                "Tell me more about this plant's light needs.",
                "How often should I water it?",
                "Is this plant safe for pets?"
            ]
            
            return ChatResponse(
                response=content,
                suggestions=suggestions
            )
        except Exception as e:
            print(f"Ollama Chat Error: {e}")
            return ChatResponse(
                response="I'm having trouble connecting to my local brain (Ollama). Please ensure it's running.",
                suggestions=["Check Ollama status"]
            )

    @staticmethod
    async def analyze_plant_health(plant_info: str, health_checks: str) -> Dict[str, Any]:
        prompt = f"""
        Analyze the health of this plant:
        {plant_info}
        
        Recent Health Checks:
        {health_checks}
        
        Provide a JSON response with:
        {{
            "health_score": float (0-100),
            "issues": [list],
            "recommendations": [list],
            "next_actions": [list]
        }}
        """
        try:
            response = ollama.generate(
                model=OllamaService.MODEL,
                prompt=prompt,
                format='json'
            )
            return json.loads(response['response'])
        except Exception as e:
            print(f"Ollama Analysis Error: {e}")
            return {
                "health_score": 50,
                "issues": ["Analysis failed"],
                "recommendations": ["Ensure Ollama is running and Llama3 is pulled"],
                "next_actions": ["Retry later"]
            }
