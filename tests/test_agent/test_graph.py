import pytest
from langchain_core.messages import HumanMessage
from bruno.agent.graph import route_by_intent, create_bruno_agent

def test_route_by_intent():
    # Test debug routing
    state = {"intent": "debug", "iteration_count": 0}
    assert route_by_intent(state) == "debug_agent"
    
    # Test research routing
    state = {"intent": "research", "iteration_count": 0}
    assert route_by_intent(state) == "research_agent"
    
    # Test direct answer routing
    state = {"intent": "direct_answer", "iteration_count": 0}
    assert route_by_intent(state) == "direct_answer"
    
    # Test loop guard
    state = {"intent": "debug", "iteration_count": 6}
    assert route_by_intent(state) == "formatter"

def test_graph_compilation(settings):
    # Just verify it compiles without errors
    agent = create_bruno_agent(settings, tools=[])
    assert agent is not None
