import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

from ..core.config import settings
from ..models.chat import ChatMessage, ChatResponse
from ..db.firestore import FirestoreDB
from .weather_service import WeatherService
from .tavily_service import TavilyService
from .plant_service import PlantService

PLANT_MIND_SYSTEM_PROMPT = """You are PlantMind, Flourish's autonomous garden agent. You are proactive,
knowledgeable, and caring about plant health.

Follow this loop for every request: understand what's being asked, decide whether a tool would
improve your answer, call at most 2 tools, then synthesize a direct, actionable answer grounded in
the user's actual garden and current data when relevant.

Available tools let you look up the user's own plants and task history, current weather for a
location, and live web search for facts that go stale (pest activity, product availability, current
events). Only call a tool when it would materially improve the answer - don't call tools for
questions you can already answer well.

Never invent completed tasks, never claim certainty you don't have, and always include safety
warnings for toxic plants or chemical treatments. Respond in a warm, encouraging tone."""

def _build_tools(user_id: str):
    @tool
    async def get_user_garden() -> str:
        """Get the current user's plants: name, species, health status, and care needs."""
        plants = await FirestoreDB.get_user_plants(user_id)
        summary = [
            {
                "name": p.get("name"),
                "species": p.get("species"),
                "health_status": p.get("health_status"),
                "location": p.get("location"),
                "sunlight_requirement": p.get("sunlight_requirement"),
                "watering_frequency_days": p.get("watering_frequency_days")
            }
            for p in plants
        ]
        return json.dumps(summary, default=str)

    @tool
    async def get_task_history() -> str:
        """Get the current user's recent care tasks, completed and pending."""
        tasks = await FirestoreDB.get_user_tasks(user_id)
        return json.dumps(tasks[:20], default=str)

    @tool
    async def get_weather(lat: float, lon: float) -> str:
        """Get current weather conditions for a location by latitude/longitude."""
        data = await WeatherService.get_weather_by_location(lat, lon)
        return json.dumps(data, default=str)

    @tool
    async def web_search(query: str) -> str:
        """Search the web for current, sourced information relevant to plant care."""
        return await TavilyService.search(query)

    return [get_user_garden, get_task_history, get_weather, web_search]

class GroqService:
    """Sole LLM backend for Flourish. Ollama has been retired - see docs/04-Rules-of-Engagement.md Rule 11."""

    @staticmethod
    def _client(json_mode: bool = False) -> ChatGroq:
        kwargs: Dict[str, Any] = {
            "model": settings.GROQ_MODEL,
            "api_key": settings.GROQ_API_KEY,
            "temperature": 0.4
        }
        if json_mode:
            kwargs["model_kwargs"] = {"response_format": {"type": "json_object"}}
        return ChatGroq(**kwargs)

    @staticmethod
    async def chat_with_ai(
        messages: List[ChatMessage],
        user_id: str,
        context: Optional[str] = None
    ) -> ChatResponse:
        """Agentic chat: reason -> optional tool call(s) -> answer -> follow-up suggestions."""
        try:
            if not settings.GROQ_API_KEY:
                raise RuntimeError("GROQ_API_KEY is not configured")

            tools = _build_tools(user_id)
            agent = create_react_agent(GroqService._client(), tools)

            lc_messages: List[Any] = [SystemMessage(content=PLANT_MIND_SYSTEM_PROMPT)]
            if context:
                lc_messages.append(SystemMessage(content=context))
            for m in messages:
                if m.role == "user":
                    lc_messages.append(HumanMessage(content=m.content))
                else:
                    lc_messages.append(AIMessage(content=m.content))

            result = await agent.ainvoke(
                {"messages": lc_messages},
                config={"recursion_limit": 8}
            )
            content = result["messages"][-1].content

            suggestions = GroqService._generate_suggestions(content, messages)
            await GroqService.update_agent_profile_summary(user_id)
            return ChatResponse(response=content, suggestions=suggestions)
        except Exception as e:
            print(f"Groq Chat Error: {e}")
            return ChatResponse(
                response="I'm having trouble reaching PlantMind right now. Please check that "
                         "GROQ_API_KEY is configured and try again shortly.",
                suggestions=["Check backend configuration", "Try again in a moment"]
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

        lowered = response.lower()
        if "water" in lowered:
            suggestions.insert(0, "How do I know if I'm overwatering?")
        if "light" in lowered or "sun" in lowered:
            suggestions.insert(0, "What are signs of too much/too little light?")
        if "fertiliz" in lowered:
            suggestions.insert(0, "What type of fertilizer should I use?")

        return suggestions[:4]

    @staticmethod
    async def analyze_plant_health(plant_info: str, health_checks: str) -> Dict[str, Any]:
        """Analyze plant health via Groq, returning structured JSON"""
        prompt = f"""
        Analyze the health of this plant:
        {plant_info}

        Recent Health Checks:
        {health_checks}

        Respond with JSON only:
        {{
            "health_score": float (0-100),
            "issues": [list of identified issues],
            "recommendations": [list of care recommendations],
            "next_actions": [list of immediate actions to take]
        }}
        """
        try:
            client = GroqService._client(json_mode=True)
            response = await client.ainvoke([HumanMessage(content=prompt)])
            return json.loads(response.content)
        except Exception as e:
            print(f"Groq Analysis Error: {e}")
            return {
                "health_score": 75,
                "issues": ["Unable to perform detailed analysis"],
                "recommendations": ["Ensure regular watering and proper light exposure"],
                "next_actions": ["Check Groq API configuration"]
            }

    @staticmethod
    async def get_plant_info_agentic(plant_name: str) -> Dict[str, Any]:
        """Agentic plant information retrieval - user types plant name, we return structured care info"""
        prompt = f"""
        Provide comprehensive care information for the plant: {plant_name}

        Respond with JSON only:
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
            client = GroqService._client(json_mode=True)
            response = await client.ainvoke([HumanMessage(content=prompt)])
            return json.loads(response.content)
        except Exception as e:
            print(f"Groq Plant Info Error: {e}")
            return {
                "common_name": plant_name,
                "scientific_name": "Unknown",
                "care_level": "moderate",
                "error": "Unable to retrieve detailed plant information"
            }

    @staticmethod
    async def analyze_document(document_text: str, analysis_type: str = "care_guide") -> Dict[str, Any]:
        """Analyze uploaded plant care documents"""
        prompt = f"""
        Analyze this plant care document and extract key information:

        {document_text[:4000]}

        Respond with JSON only:
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
            client = GroqService._client(json_mode=True)
            response = await client.ainvoke([HumanMessage(content=prompt)])
            return json.loads(response.content)
        except Exception as e:
            print(f"Groq Document Analysis Error: {e}")
            return {
                "summary": "Document analysis failed",
                "key_points": [],
                "error": str(e)
            }

    @staticmethod
    async def generate_recommendations(user_id: str, count: int = 3) -> List[Dict[str, Any]]:
        """
        Generate personalized plant recommendations grounded in the user's own garden,
        agent_profile, and (optionally) live weather/web search - see docs/01-PRD.md §4.5.
        Persists each recommendation to the `recommendations` collection.
        """
        if not settings.GROQ_API_KEY:
            return []

        try:
            profile = await FirestoreDB.get_profile(user_id) or {}
            plants = await FirestoreDB.get_user_plants(user_id)
            agent_profile = profile.get("agent_profile") or {}
            avoided = (agent_profile.get("recommendation_preferences") or {}).get("avoided_plants", [])
            owned_species = [p.get("species") or p.get("name") for p in plants]

            prompt = f"""
            The user's current garden (species/names): {json.dumps(owned_species)}
            Their care habit summary: {agent_profile.get("summary") or "No history yet."}
            Plants to avoid recommending (already dismissed by this user): {json.dumps(avoided)}

            Recommend {count} NEW plants (not already in their garden, not in the avoided list)
            that would thrive for this specific user. Use the web_search and get_weather tools
            only if they would materially improve a suggestion's accuracy - don't over-use them.

            When ready, respond with ONLY a JSON array (no prose, no markdown fences):
            [{{
                "plant_name": "string",
                "scientific_name": "string",
                "reasoning": "string - why this fits this user's garden specifically",
                "difficulty": "easy|moderate|advanced",
                "warnings": ["string", ...],
                "sources": ["string url", ...]
            }}]
            """

            tools = _build_tools(user_id)
            agent = create_react_agent(GroqService._client(), tools)
            result = await agent.ainvoke(
                {"messages": [SystemMessage(content=PLANT_MIND_SYSTEM_PROMPT), HumanMessage(content=prompt)]},
                config={"recursion_limit": 8}
            )
            content = result["messages"][-1].content
            parsed = GroqService._extract_json_array(content)

            recommendations = []
            for item in parsed[:count]:
                image_url = None
                try:
                    image_url = await PlantService.fetch_plant_image(
                        item.get("plant_name", ""), item.get("scientific_name", "")
                    )
                except Exception:
                    pass

                rec = await FirestoreDB.create_recommendation({
                    "user_id": user_id,
                    "plant_name": item.get("plant_name", "Unknown"),
                    "scientific_name": item.get("scientific_name", ""),
                    "image_url": image_url,
                    "reasoning": item.get("reasoning", ""),
                    "difficulty": item.get("difficulty", "moderate"),
                    "warnings": item.get("warnings", []),
                    "sources": item.get("sources", []),
                    "status": "pending"
                })
                recommendations.append(rec)

            return recommendations
        except Exception as e:
            print(f"Groq Recommendation Error: {e}")
            return []

    @staticmethod
    def _extract_json_array(content: str) -> List[Dict[str, Any]]:
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            start = content.find('[')
            end = content.rfind(']')
            if start != -1 and end != -1:
                try:
                    return json.loads(content[start:end + 1])
                except json.JSONDecodeError:
                    return []
            return []

    @staticmethod
    async def update_agent_profile_summary(user_id: str) -> None:
        """
        Refresh profiles.agent_profile from the user's current garden + task history.
        Deterministic (no extra LLM call) so it's cheap to run after every meaningful
        interaction - see docs/06-Phase-Tracker.md Phase 2 known gap.
        """
        try:
            profile = await FirestoreDB.get_profile(user_id)
            if not profile:
                return

            plants = await FirestoreDB.get_user_plants(user_id)
            tasks = await FirestoreDB.get_user_tasks(user_id)

            low_light = sum(1 for p in plants if "low" in (p.get("sunlight_requirement") or "").lower())
            pet_safe = sum(1 for p in plants if (p.get("toxicity") or "").lower() == "non-toxic")
            outdoor = sum(1 for p in plants if (p.get("plant_type") or "").lower() == "outdoor")

            completed = [t for t in tasks if t.get("completed")]
            watering_done = [t for t in completed if t.get("task_type") == "watering"]
            fertilizing_done = [t for t in completed if t.get("task_type") == "fertilizing"]

            summary = (
                f"{len(plants)} plants in the garden ({low_light} low-light, {pet_safe} pet-safe, "
                f"{outdoor} outdoor). {len(completed)} of {len(tasks)} tasks completed."
            )

            agent_profile = profile.get("agent_profile") or {}
            agent_profile.update({
                "summary": summary,
                "garden_composition": {
                    "low_light_plants": low_light,
                    "pet_safe_plants": pet_safe,
                    "outdoor_plants": outdoor
                },
                "care_habits": {
                    "watering_consistency": "high" if len(watering_done) >= 3 else "developing",
                    "fertilizing_consistency": "high" if len(fertilizing_done) >= 1 else "developing",
                    "health_check_frequency": "medium"
                },
                "updated_at": datetime.now().isoformat()
            })

            await FirestoreDB.update_profile(user_id, {"agent_profile": agent_profile})
        except Exception as e:
            print(f"agent_profile update error: {e}")
