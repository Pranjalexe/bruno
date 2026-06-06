"""
Simple Q&A node for factual questions.
"""
from langchain_core.messages import SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from bruno.agent.state import BrunoState
from bruno.config import get_settings

SYSTEM_PROMPT = """You are Bruno, a helpful developer assistant. Answer the following
question concisely and accurately. If you're not sure, say so."""

def direct_answer_node(state: BrunoState) -> dict:
    settings = get_settings()
    llm = ChatGoogleGenerativeAI(model=settings.default_model, temperature=0, api_key=settings.gemini_api_key)

    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = llm.invoke(messages)

    return {
        "messages": [response],
        "final_response": str(response.content)
    }
