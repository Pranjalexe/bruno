"""
Specialized research agent node.
"""
from langchain_core.messages import SystemMessage

from bruno.agent.state import BrunoState

SYSTEM_PROMPT = """You are Bruno, a research assistant for developers.
    
Your approach:
1. Search the local knowledge base for relevant documentation
2. Search the web for up-to-date information
3. Synthesize findings into a clear, structured summary
4. Compare pros/cons when the query involves technology choices
5. Include code examples when relevant

Always cite sources in your response."""

def get_research_agent_node(llm_with_tools):
    def research_agent_node(state: BrunoState) -> dict:
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
        response = llm_with_tools.invoke(messages)
        return {
            "messages": [response],
            "iteration_count": state.get("iteration_count", 0) + 1
        }
    return research_agent_node
