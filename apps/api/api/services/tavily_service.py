from typing import Any, Dict, List
from ..core.config import settings

class TavilyService:
    """Web search tool used by GroqService's agent for grounded, current information."""

    @staticmethod
    async def search(query: str, max_results: int = 3) -> str:
        if not settings.TAVILY_API_KEY:
            return "Web search is unavailable right now (no TAVILY_API_KEY configured)."

        try:
            from langchain_tavily import TavilySearch

            search_tool = TavilySearch(max_results=max_results, tavily_api_key=settings.TAVILY_API_KEY)
            result = await search_tool.ainvoke({"query": query})
            return str(result)
        except Exception as e:
            print(f"Tavily search error: {e}")
            return f"Web search failed: {e}"

    @staticmethod
    async def search_raw(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Structured (non-summarized) search results - [{title, url, content}, ...] - for
        callers that curate the results themselves with rule-based logic instead of
        handing them to an LLM (see plant_lookup_service.py's Explore lookup).
        """
        if not settings.TAVILY_API_KEY:
            return []
        try:
            from langchain_tavily import TavilySearch

            search_tool = TavilySearch(max_results=max_results, tavily_api_key=settings.TAVILY_API_KEY)
            result = await search_tool.ainvoke({"query": query})
            if isinstance(result, dict):
                return result.get("results") or []
            return []
        except Exception as e:
            print(f"Tavily raw search error: {e}")
            return []
