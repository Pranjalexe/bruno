"""
Web search tool using a free search API (DuckDuckGo).
"""
from langchain_core.tools import tool


@tool
def web_search(query: str, max_results: int = 5) -> str:
    """Search the web for information about a topic.
    
    Args:
        query: The search query
        max_results: Maximum number of results (default 5)
    
    Returns:
        Formatted string with search results.
    """
    try:
        from langchain_community.tools import DuckDuckGoSearchRun
        search = DuckDuckGoSearchRun()
        # The DuckDuckGoSearchRun handles the query directly.
        # It doesn't natively take max_results in the run method, but it limits internally.
        return search.invoke(query)
    except ImportError:
        return "Error: duckduckgo-search package is missing. Please install it."
    except Exception as e:
        return f"Error performing web search: {e}"
