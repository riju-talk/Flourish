import asyncio
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_tool_calling_agent

from ..core.config import settings
from ..models.chat import ChatMessage, ChatResponse
from ..db.firestore import FirestoreDB
from .weather_service import WeatherService
from .tavily_service import TavilyService
from .plant_service import PlantService
from .perenual_service import PerenualService

PLANT_MIND_SYSTEM_PROMPT = """You are PlantMind, Flourish's autonomous garden agent. You are proactive,
knowledgeable, and caring about plant health.

Follow this loop for every request: understand what's being asked, decide whether a tool would
improve your answer, call at most 2 tools, then synthesize a direct, actionable answer grounded in
the user's actual garden and current data when relevant.

Available tools let you look up the user's own plants and task history, current weather for a
location, live web search for facts that go stale (pest activity, product availability, current
events), and a real plant-care database (Perenual) for authoritative watering/sunlight facts about
a specific species - prefer that over guessing when a question is about a named plant's care needs.
Only call a tool when it would materially improve the answer - don't call tools for questions you
can already answer well.

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

    @tool
    async def get_plant_care_facts(plant_name: str) -> str:
        """
        Get authoritative watering frequency and sunlight requirement for a named plant
        species from the Perenual plant-care database. Use this instead of guessing
        when a question is specifically about how to care for a named plant.
        """
        info = await PerenualService.get_care_info(plant_name)
        if not info:
            return f"No Perenual data found for '{plant_name}'."
        return json.dumps(info, default=str)

    return [get_user_garden, get_task_history, get_weather, web_search, get_plant_care_facts]

class GroqService:
    """
    Sole LLM backend for Flourish. Ollama has been retired - see
    docs/04-Rules-of-Engagement.md Rule 11. The agent is built on plain LangChain
    (langchain.agents.AgentExecutor + create_tool_calling_agent) - LangGraph is not
    used anywhere in this codebase.
    """

    @staticmethod
    def _client(json_mode: bool = False) -> ChatGroq:
        kwargs: Dict[str, Any] = {
            "model": settings.GROQ_MODEL,
            "api_key": settings.GROQ_API_KEY,
            "temperature": 0.4
        }
        if json_mode:
            kwargs["model_kwargs"] = {"response_format": {"type": "json_object"}}
            # get_plant_info_agentic's schema (10+ nested objects/arrays) routinely got
            # cut off mid-document at the default token limit, which Groq's JSON
            # validator then rejects outright ("max completion tokens reached before
            # generating a valid document") - the caller's fallback silently ate every
            # field this was supposed to fill in.
            kwargs["max_tokens"] = 2048
            # The configured model is a reasoning model (emits a <think>...</think>
            # block before its actual answer). For anything beyond a trivial prompt,
            # that reasoning alone regularly exceeds the whole max_tokens budget,
            # leaving zero tokens for the actual JSON - which Groq's json_object
            # validator then rejects outright ("Failed to validate JSON" with an
            # empty failed_generation, since nothing but reasoning was ever
            # generated). reasoning_effort="none" skips the thinking phase entirely
            # for these structured-extraction calls, which don't need multi-step
            # deliberation anyway; reasoning_format="hidden" is kept as a second
            # layer so a stray reasoning block never leaks into the JSON output.
            kwargs["reasoning_format"] = "hidden"
            kwargs["reasoning_effort"] = "none"
        return ChatGroq(**kwargs)

    @staticmethod
    def _build_agent_executor(user_id: str, system_prompt: str) -> AgentExecutor:
        """
        Build a tool-calling agent bound to this user's tools. AgentExecutor's
        reason -> act -> observe loop is capped by max_iterations so a turn can't run
        away calling tools indefinitely - see PLANT_MIND_SYSTEM_PROMPT's "at most 2
        tools" guidance.
        """
        tools = _build_tools(user_id)
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ])
        agent = create_tool_calling_agent(GroqService._client(), tools, prompt)
        return AgentExecutor(agent=agent, tools=tools, max_iterations=4, handle_parsing_errors=True)

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
            if not messages:
                raise ValueError("messages must contain at least the user's latest turn")

            system_prompt = PLANT_MIND_SYSTEM_PROMPT
            memory = await GroqService._agent_memory_context(user_id)
            if memory:
                system_prompt += f"\n\nWhat you remember about this user: {memory}"
            if context:
                system_prompt += f"\n\nAdditional context: {context}"

            chat_history: List[BaseMessage] = []
            for m in messages[:-1]:
                if m.role == "user":
                    chat_history.append(HumanMessage(content=m.content))
                else:
                    chat_history.append(AIMessage(content=m.content))

            executor = GroqService._build_agent_executor(user_id, system_prompt)
            result = await executor.ainvoke({
                "input": messages[-1].content,
                "chat_history": chat_history
            })
            content = result["output"]

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
    async def curate_plant_lookup(
        plant_name: str,
        perenual: Optional[Dict[str, Any]],
        tavily_results: List[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        """
        Explore/Plant Lookup synthesis: Perenual (structured, deterministic) and Tavily
        (live web search results) are the only sources of fact - this call's only job
        is to read both and write up one coherent, well-organized profile in the shape
        the Explore UI renders. It must not invent facts beyond what's given, and must
        say so explicitly (rather than guessing) wherever neither source covers a
        field. Returns None on any failure so the caller can fall back to
        plant_lookup_service.curate_plant_info's deterministic keyword extraction -
        this is an upgrade over that fallback's quality, not a replacement for its
        reliability.
        """
        perenual_json = json.dumps(perenual) if perenual else "null (no match found - be extra careful not to assume facts about this specific plant)"
        # Trim each result's content - only enough for the model to ground itself, not
        # so much that a handful of results blow the completion budget before the
        # model finishes writing valid JSON (see the max_tokens comment in _client).
        search_snippets = "\n\n".join(
            f"[{i+1}] {r.get('title','')}\n{(r.get('content') or '')[:600]}\nURL: {r.get('url','')}"
            for i, r in enumerate(tavily_results[:5])
        ) or "No web search results available."

        prompt = f"""
        A user searched for the plant: "{plant_name}"

        Structured data from Perenual (a plant-care database) for the best species match found:
        {perenual_json}

        Live web search results:
        {search_snippets}

        Using ONLY the information above, write a curated care profile for this plant. If the
        Perenual data above appears to describe a DIFFERENT plant than what the search results and
        the user's query are actually about, ignore the Perenual data entirely and rely on the
        search results instead - do not present facts about the wrong species. If a field isn't
        covered by either source, say "See sources below" (for care fields) or leave the array
        empty rather than inventing a plausible-sounding answer.

        Respond with JSON only, matching this exact shape:
        {{
            "common_name": "string",
            "scientific_name": "string",
            "care_level": "easy|moderate|difficult",
            "watering": {{"frequency": "string, e.g. 'Every 7 days'", "amount": "string", "tips": "string"}},
            "sunlight": {{"requirement": "string, e.g. 'Bright, indirect'", "details": "string"}},
            "fertilizing": {{"frequency": "string", "type": "string"}},
            "toxicity": {{"pets": "toxic|safe|unknown", "humans": "toxic|safe|unknown", "details": "string"}},
            "environment": {{"native_habitat": "string", "grows_indoors": true}},
            "common_issues": ["up to 4 short strings"],
            "propagation": ["up to 4 short strings, e.g. 'stem cutting'"],
            "interesting_facts": ["up to 3 short strings"]
        }}
        """
        try:
            client = GroqService._client(json_mode=True)
            response = await client.ainvoke([HumanMessage(content=prompt)])
            curated = json.loads(response.content)
            # Sources are the caller's own Tavily URLs, not anything the model wrote -
            # never trust an LLM to reproduce a URL correctly.
            curated["sources"] = [r.get("url") for r in tavily_results if r.get("url")][:5]
            return curated
        except Exception as e:
            print(f"Groq Plant Lookup Curation Error: {e}")
            return None

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

            executor = GroqService._build_agent_executor(user_id, PLANT_MIND_SYSTEM_PROMPT)
            result = await executor.ainvoke({"input": prompt, "chat_history": []})
            content = result["output"]
            parsed = GroqService._extract_json_array(content)

            items = parsed[:count]
            # One Unsplash search per item is independent of the others - run them
            # concurrently instead of one-by-one so N picks don't cost N sequential
            # round-trips.
            image_urls = await asyncio.gather(*[
                PlantService.fetch_plant_image(item.get("plant_name", ""), item.get("scientific_name", ""))
                for item in items
            ])

            recommendations = []
            for item, image_url in zip(items, image_urls):
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

            await GroqService._enforce_recommendation_cap(user_id)

            return recommendations
        except Exception as e:
            print(f"Groq Recommendation Error: {e}")
            return []

    MAX_PENDING_RECOMMENDATIONS = 10

    @staticmethod
    async def _enforce_recommendation_cap(user_id: str) -> None:
        """
        Keep at most MAX_PENDING_RECOMMENDATIONS pending. Once full, the oldest pending
        ones rotate out as "expired" (not added to avoided_plants) so the pool stays
        fresh as the garden expands, and rotated-out plants can resurface again later -
        only an explicit dismiss should permanently avoid a plant.
        """
        pending = await FirestoreDB.get_user_recommendations(user_id, status="pending")
        overflow = len(pending) - GroqService.MAX_PENDING_RECOMMENDATIONS
        if overflow <= 0:
            return

        pending.sort(key=lambda r: str(r.get("created_at") or ""))
        for rec in pending[:overflow]:
            await FirestoreDB.update_recommendation(rec["id"], {"status": "expired"})

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
    async def _agent_memory_context(user_id: str) -> str:
        """
        PlantMind's persistent per-user memory: profiles.agent_profile (see
        update_agent_profile_summary) is a durable, deterministic summary of this
        user's garden and care habits that survives across sessions and devices -
        unlike chat_history, which only covers the current conversation. Every agent
        call (chat here, and generate_recommendations) reads it back in so PlantMind
        "remembers" the user without re-deriving everything from raw Firestore data
        or, worse, forgetting entirely between conversations.
        """
        profile = await FirestoreDB.get_profile(user_id)
        if not profile:
            return ""
        agent_profile = profile.get("agent_profile") or {}
        parts = []
        if agent_profile.get("summary"):
            parts.append(agent_profile["summary"])
        prefs = agent_profile.get("recommendation_preferences") or {}
        if prefs.get("avoided_plants"):
            parts.append(f"Has previously dismissed: {', '.join(prefs['avoided_plants'])}.")
        if prefs.get("preferred_traits"):
            parts.append(f"Seems to prefer: {', '.join(prefs['preferred_traits'])}.")
        return " ".join(parts)

    @staticmethod
    async def update_agent_profile_summary(user_id: str) -> None:
        """
        Refresh profiles.agent_profile from the user's current garden + task history -
        the persistent memory store _agent_memory_context reads back on every future
        agent call. Deterministic (no extra LLM call) so it's cheap to run after every
        meaningful interaction (chat turns, a plant being added, a task completed) -
        see docs/06-Phase-Tracker.md Phase 2 known gap.
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
