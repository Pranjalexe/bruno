"""
RAG search tool for querying the local ChromaDB knowledge base.
"""
from langchain_core.tools import tool

from bruno.config import get_settings
from bruno.rag.store import BrunoVectorStore


@tool
def rag_search(query: str, collection: str = "knowledge_base", n_results: int = 5) -> str:
    """Search the local knowledge base for documents relevant to the query.
    
    Args:
        query: The search query
        collection: Which collection to search ("knowledge_base", "error_logs", "project_docs")
        n_results: Number of results to return (default 5)
    
    Returns:
        Formatted string with matching document chunks and their sources.
    """
    settings = get_settings()
    store = BrunoVectorStore(settings.data_dir)

    docs = store.query(query=query, collection_name=collection, n_results=n_results)

    if not docs:
        return "No relevant documents found."

    results = []
    for doc in docs:
        source = doc.metadata.get("source", "unknown")
        results.append(f"--- Source: {source} ---\n{doc.page_content}\n")

    return "\n".join(results)
