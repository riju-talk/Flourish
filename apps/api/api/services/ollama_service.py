import ollama
import json
from typing import List, Dict, Any, Optional
from ..models.plant import Plant, HealthCheckItem, PlantAnalysis
from ..models.chat import ChatMessage, ChatResponse
from ..core.config import settings

class OllamaService:
    MODEL = settings.OLLAMA_MODEL
    BASE_URL = settings.OLLAMA_BASE_URL

    @staticmethod
    async def chat_with_ai(messages: List[ChatMessage], context: Optional[str] = None) -> ChatResponse:
        """
        Chat with Ollama LLM using provided messages and optional context
        """
        try:
            # Add system context if provided
            ollama_messages = []
            if context:
                ollama_messages.append({"role": "system", "content": context})
            
            ollama_messages.extend([{"role": m.role, "content": m.content} for m in messages])
            
            client = ollama.Client(host=OllamaService.BASE_URL)
            response = client.chat(
                model=OllamaService.MODEL,
                messages=ollama_messages,
            )
            
            content = response['message']['content']
            
            # Generate contextual follow-up suggestions
            suggestions = OllamaService._generate_suggestions(content, messages)
            
            return ChatResponse(
                response=content,
                suggestions=suggestions
            )
        except Exception as e:
            print(f"Ollama Chat Error: {e}")
            return ChatResponse(
                response="I'm having trouble connecting to Ollama. Please ensure Ollama is running locally with the llama3 model installed. Run: `ollama pull llama3`",
                suggestions=["Check Ollama status", "Install llama3 model"]
            )

    @staticmethod
    def _generate_suggestions(response: str, messages: List[ChatMessage]) -> List[str]:
        """Generate contextual follow-up questions"""
        suggestions = [
            "Tell me more about this plant's care requirements",
            "What are common problems with this plant?",
            "How can I propagate this plant?",
            "Is this plant safe for pets?"
        ]
        
        # Contextual suggestions based on response content
        if "water" in response.lower():
            suggestions.insert(0, "How do I know if I'm overwatering?")
        if "light" in response.lower() or "sun" in response.lower():
            suggestions.insert(0, "What are signs of too much/too little light?")
        if "fertiliz" in response.lower():
            suggestions.insert(0, "What type of fertilizer should I use?")
            
        return suggestions[:4]  # Return top 4 suggestions

    @staticmethod
    async def analyze_plant_health(plant_info: str, health_checks: str) -> Dict[str, Any]:
        """Analyze plant health using Ollama"""
        prompt = f"""
        Analyze the health of this plant:
        {plant_info}
        
        Recent Health Checks:
        {health_checks}
        
        Provide a JSON response with:
        {{
            "health_score": float (0-100),
            "issues": [list of identified issues],
            "recommendations": [list of care recommendations],
            "next_actions": [list of immediate actions to take]
        }}
        """
        try:
            client = ollama.Client(host=OllamaService.BASE_URL)
            response = client.generate(
                model=OllamaService.MODEL,
                prompt=prompt,
                format='json'
            )
            return json.loads(response['response'])
        except Exception as e:
            print(f"Ollama Analysis Error: {e}")
            return {
                "health_score": 75,
                "issues": ["Unable to perform detailed analysis"],
                "recommendations": ["Ensure regular watering and proper light exposure"],
                "next_actions": ["Check Ollama service status"]
            }

    @staticmethod
    async def get_plant_info_agentic(plant_name: str) -> Dict[str, Any]:
        """
        Agentic plant information retrieval - user types plant name,
        we use LLM to extract comprehensive information
        """
        prompt = f"""
        Provide comprehensive care information for the plant: {plant_name}
        
        Return a detailed JSON with:
        {{
            "common_name": "string",
            "scientific_name": "string",
            "care_level": "easy|moderate|difficult",
            "watering": {{"frequency": "string", "amount": "string", "tips": "string"}},
            "sunlight": {{"requirement": "string", "details": "string"}},
            "temperature": {{"min": number, "max": number, "ideal": "string"}},
            "humidity": {{"requirement": "string", "percentage": "string"}},
            "soil": {{"type": "string", "ph": "string"}},
            "fertilizing": {{"frequency": "string", "type": "string"}},
            "growth": {{"rate": "string", "max_size": "string"}},
            "toxicity": {{"pets": "safe|toxic", "humans": "safe|toxic", "details": "string"}},
            "common_issues": ["list of common problems"],
            "propagation": ["list of propagation methods"],
            "interesting_facts": ["list of interesting facts"]
        }}
        """
        try:
            client = ollama.Client(host=OllamaService.BASE_URL)
            response = client.generate(
                model=OllamaService.MODEL,
                prompt=prompt,
                format='json'
            )
            return json.loads(response['response'])
        except Exception as e:
            print(f"Ollama Plant Info Error: {e}")
            return {
                "common_name": plant_name,
                "scientific_name": "Unknown",
                "care_level": "moderate",
                "error": "Unable to retrieve detailed plant information"
            }

    @staticmethod
    async def analyze_document(document_text: str, analysis_type: str = "care_guide") -> Dict[str, Any]:
        """
        Analyze uploaded plant care documents
        """
        prompt = f"""
        Analyze this plant care document and extract key information:
        
        {document_text[:4000]}  # Limit text length
        
        Provide a JSON response with:
        {{
            "summary": "brief summary of the document",
            "key_points": ["list of key care points"],
            "watering_schedule": "extracted watering info",
            "fertilizing_schedule": "extracted fertilizing info",
            "light_requirements": "extracted light info",
            "warnings": ["any important warnings or cautions"],
            "action_items": ["suggested actions based on the document"]
        }}
        """
        try:
            client = ollama.Client(host=OllamaService.BASE_URL)
            response = client.generate(
                model=OllamaService.MODEL,
                prompt=prompt,
                format='json'
            )
            return json.loads(response['response'])
        except Exception as e:
            print(f"Ollama Document Analysis Error: {e}")
            return {
                "summary": "Document analysis failed",
                "key_points": [],
                "error": str(e)
            }
