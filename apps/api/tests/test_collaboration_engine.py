import pytest
import asyncio
from src.schemas.cognitive import CollaborationState, AgentMessage
from src.services.collaboration.taxonomy import CollaborationStrategy
from src.services.collaboration.heuristics import resolve_deadlocks
from src.services.collaboration.engine import CollaborationLLMService

def test_resolve_deadlocks():
    # Setup state with a massive unresolved debate
    state = CollaborationState(
        strategy=CollaborationStrategy.DEBATE_AND_CRITIQUE.value,
        active_agents=["agent_1", "agent_2"],
        agent_outputs=[
            AgentMessage(agent_role="agent_1", content="Point 1"),
            AgentMessage(agent_role="agent_2", content="Counterpoint 1"),
            AgentMessage(agent_role="agent_1", content="Point 2"),
            AgentMessage(agent_role="agent_2", content="Counterpoint 2"),
            AgentMessage(agent_role="agent_1", content="Point 3"),
        ],
        synthesized_insight=None,
        confidence=0.8
    )
    
    result = resolve_deadlocks(state)
    
    # Assert a forced resolution was injected
    assert result.synthesized_insight is not None
    assert "Forced resolution" in result.synthesized_insight

@pytest.mark.asyncio
async def test_collaboration_llm_service():
    service = CollaborationLLMService()
    
    # Mock deep intent
    class MockIntent:
        depth_level = "deep"
        
    result = await service.orchestrate_collaboration(
        raw_input="What is the meaning of it all?",
        intent=MockIntent(), thought=None, graph=None, orchestration=None
    )
    
    assert result.strategy == CollaborationStrategy.DEBATE_AND_CRITIQUE.value
    assert len(result.active_agents) > 1
    assert result.synthesized_insight is not None
