"""
Classifies the user's intent.
"""
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from bruno.agent.state import BrunoState
from bruno.config import get_settings

SYSTEM_PROMPT = """You are an intent classifier. Given a user's query, classify it as:
- 'debug': The user is asking about an error, bug, exception, or wants to troubleshoot something.
- 'research': The user wants to learn about a topic, compare technologies, or understand a concept.
- 'direct_answer': The user has a simple factual question that doesn't require tools or context.

Respond with ONLY the intent label, nothing else."""

def classifier_node(state: BrunoState) -> dict:
    settings = get_settings()
    llm = ChatGoogleGenerativeAI(model=settings.default_model, temperature=0, api_key=settings.gemini_api_key)

    # If intent was already forced (e.g. via CLI command explicitly), don't re-classify
    if state.get("intent"):
        return {}

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=state["user_query"])
    ]

    response = llm.invoke(messages)
    intent = str(response.content).strip().lower()

    # Validation fallback
    if intent not in ["debug", "research", "direct_answer"]:
        intent = "direct_answer"

    return {"intent": intent}
