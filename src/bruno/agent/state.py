"""
Agent state schema for the Bruno LangGraph workflow.
"""
from typing import Annotated, Any

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class BrunoState(TypedDict):
    # Conversation history with proper deduplication reducer
    messages: Annotated[list[BaseMessage], add_messages]

    # Classified intent: "debug", "research", "direct_answer"
    intent: str | None

    # The original query string
    user_query: str

    # RAG retrieved context text
    retrieved_context: list[str]

    # Results from tools (MCP, web, RAG)
    tool_results: dict[str, Any]

    # The final formatted response for the CLI
    final_response: str

    # Any error that occurred
    error: str | None

    # Guard against infinite tool loops
    iteration_count: int
