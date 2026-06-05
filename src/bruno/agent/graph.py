"""
LangGraph StateGraph assembly for Bruno.
"""
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from bruno.agent.nodes.classifier import classifier_node
from bruno.agent.nodes.debug_agent import get_debug_agent_node
from bruno.agent.nodes.direct_answer import direct_answer_node
from bruno.agent.nodes.formatter import formatter_node
from bruno.agent.nodes.research_agent import get_research_agent_node
from bruno.agent.state import BrunoState
from bruno.config import BrunoSettings


def route_by_intent(state: BrunoState) -> str:
    # iteration limit guard
    if state.get("iteration_count", 0) > 5:
        return "formatter"

    intent = state.get("intent")
    if intent == "debug":
        return "debug_agent"
    elif intent == "research":
        return "research_agent"
    else:
        return "direct_answer"

def create_bruno_agent(settings: BrunoSettings, tools: list[BaseTool]):
    """
    Creates and compiles the Bruno agent graph.
    """
    llm = ChatOpenAI(model=settings.default_model, temperature=0, api_key=settings.openai_api_key)
    if tools:
        llm_with_tools = llm.bind_tools(tools)
    else:
        llm_with_tools = llm

    builder = StateGraph(BrunoState)

    # Add nodes
    builder.add_node("classifier", classifier_node)
    builder.add_node("debug_agent", get_debug_agent_node(llm_with_tools))
    builder.add_node("research_agent", get_research_agent_node(llm_with_tools))
    builder.add_node("direct_answer", direct_answer_node)
    builder.add_node("formatter", formatter_node)

    if tools:
        builder.add_node("tools", ToolNode(tools))

    # Edges
    builder.add_edge(START, "classifier")

    builder.add_conditional_edges(
        "classifier",
        route_by_intent,
        {
            "debug_agent": "debug_agent",
            "research_agent": "research_agent",
            "direct_answer": "direct_answer",
            "formatter": "formatter"
        }
    )

    if tools:
        builder.add_conditional_edges("debug_agent", tools_condition, {"tools": "tools", END: "formatter"})
        builder.add_conditional_edges("research_agent", tools_condition, {"tools": "tools", END: "formatter"})

        # Tools go back to the caller agent.
        # Since tools_condition doesn't track caller in basic setup, we use a custom router or route back to intent
        def route_after_tools(state: BrunoState) -> str:
            if state.get("iteration_count", 0) > 5:
                return "formatter"
            if state.get("intent") == "debug":
                return "debug_agent"
            return "research_agent"

        builder.add_conditional_edges("tools", route_after_tools)
    else:
        builder.add_edge("debug_agent", "formatter")
        builder.add_edge("research_agent", "formatter")

    builder.add_edge("direct_answer", "formatter")
    # Ensure the directory exists
    db_path = settings.data_dir / "checkpoints.db"
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    
    # Use SqliteSaver
    conn = sqlite3.connect(db_path, check_same_thread=False)
    memory = SqliteSaver(conn)
    return builder.compile(checkpointer=memory)
