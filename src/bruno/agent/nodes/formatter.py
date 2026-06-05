"""
Formats the agent's final response.
"""
from bruno.agent.state import BrunoState


def formatter_node(state: BrunoState) -> dict:
    last_message = state["messages"][-1]

    return {
        "final_response": last_message.content
    }
