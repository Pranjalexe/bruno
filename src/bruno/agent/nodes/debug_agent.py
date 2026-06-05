"""
Specialized debugging agent node.
"""
from langchain_core.messages import SystemMessage

from bruno.agent.state import BrunoState

SYSTEM_PROMPT = """You are Bruno, an expert debugging assistant. You help developers diagnose and fix errors.
    
Your approach:
1. First, search the local knowledge base for similar past errors
2. If needed, read relevant local files (config, logs) for context
3. Check environment variables if the error might be config-related
4. Search the web for solutions if local context is insufficient
5. Provide a clear, actionable diagnosis with fix suggestions

Always cite sources (file paths, URLs) in your response."""

def get_debug_agent_node(llm_with_tools):
    def debug_agent_node(state: BrunoState) -> dict:
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
        response = llm_with_tools.invoke(messages)
        return {
            "messages": [response],
            "iteration_count": state.get("iteration_count", 0) + 1
        }
    return debug_agent_node
