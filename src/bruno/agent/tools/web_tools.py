"""
Web search tool using Tavily API.
"""
from langchain_core.tools import tool

from bruno.config import get_settings


@tool
def web_search(query: str, max_results: int = 5) -> str:
    """Search the web for information about a topic using Tavily.
    
    Args:
        query: The search query
        max_results: Maximum number of results (default 5)
    
    Returns:
        Formatted string with search results.
    """
    settings = get_settings()
    if not settings.tavily_api_key:
        return "Error: BRUNO_TAVILY_API_KEY is not set. Run `bruno config init` to set it."

    try:
        from langchain_community.tools.tavily_search import TavilySearchResults
        search = TavilySearchResults(
            max_results=max_results,
            tavily_api_key=settings.tavily_api_key
        )
        return str(search.invoke(query))
    except Exception as e:
        return f"Error performing web search: {e}"
