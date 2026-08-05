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
