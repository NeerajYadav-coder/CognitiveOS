import pytest
import asyncio
from src.schemas.cognitive import ResearchState, ExplorationTree, ResearchNode, KnowledgeGap
from src.services.research.heuristics import enforce_bounded_exploration, detect_circular_inquiry, flag_speculative_synthesis
from src.services.research.engine import ResearchLLMService

def test_enforce_bounded_exploration():
    # Setup state with deep and overflow branches
    state = ResearchState(
        research_mode="exploratory",
        research_tree=ExplorationTree(
            root_inquiry="Test",
            branches=[
                ResearchNode(id="1", inquiry="Deep", depth_level=10, status="pending"),
                ResearchNode(id="2", inquiry="Ok", depth_level=1, status="pending"),
                ResearchNode(id="3", inquiry="Overflow", depth_level=1, status="pending"),
                ResearchNode(id="4", inquiry="Overflow", depth_level=1, status="pending"),
                ResearchNode(id="5", inquiry="Overflow", depth_level=1, status="pending"),
                ResearchNode(id="6", inquiry="Overflow", depth_level=1, status="pending"),
            ]
        ),
        confidence=0.9
    )
    
    result = enforce_bounded_exploration(state)
    
    # Assert depth limit (depth > 3 is abandoned)
    assert result.research_tree.branches[0].status == "abandoned"
    # Assert branch count limit (index >= 5 is abandoned)
    assert result.research_tree.branches[5].status == "abandoned"

def test_detect_circular_inquiry():
    state = ResearchState(
        research_mode="exploratory",
        research_tree=ExplorationTree(
            root_inquiry="Test",
            branches=[
                ResearchNode(id="1", inquiry="Duplicate", depth_level=1, status="pending"),
                ResearchNode(id="2", inquiry="duplicate", depth_level=1, status="pending"),
                ResearchNode(id="3", inquiry="Unique", depth_level=1, status="pending"),
            ]
        ),
        confidence=0.9
    )
    
    result = detect_circular_inquiry(state)
    
    # Assert duplicates removed
    assert len(result.research_tree.branches) == 2

def test_flag_speculative_synthesis():
    state = ResearchState(
        research_mode="exploratory",
        research_tree=ExplorationTree(root_inquiry="Test", branches=[]),
        synthesized_understanding="This is definitively certain.",
        confidence=0.4
    )
    
    result = flag_speculative_synthesis(state)
    
    # Assert warning injected
    assert "[NOTE: This synthesis has low confidence" in result.synthesized_understanding

@pytest.mark.asyncio
async def test_research_llm_service():
    service = ResearchLLMService()
    
    result = await service.conduct_research(
        raw_input="Why are we here?",
        intent=None, thought=None, graph=None, collaboration=None
    )
    
    assert result.research_mode == "philosophical_exploration"
    assert len(result.research_tree.branches) > 0
    assert len(result.knowledge_gaps) > 0
