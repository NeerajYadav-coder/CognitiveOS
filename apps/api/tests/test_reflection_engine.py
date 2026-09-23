import pytest
import asyncio
from src.schemas.cognitive import CognitiveReflection, ReflectionSummary
from src.services.reflection.heuristics import protect_against_diagnosis, reframe_blind_spots
from src.services.reflection.engine import ReflectionLLMService

def test_protect_against_diagnosis():
    # Setup an LLM reflection that accidentally diagnosed the user
    reflection = CognitiveReflection(
        reflection_summary=ReflectionSummary(
            dominant_themes=["Philosophy"],
            exploration_trends=["User seems depressed and anxious about the future."]
        ),
        confidence=0.9
    )
    
    result = protect_against_diagnosis(reflection)
    
    # Assert diagnostic terms were scrubbed
    trend = result.reflection_summary.exploration_trends[0]
    assert "depressed" not in trend
    assert "anxious" not in trend
    assert "exploration" in trend

def test_reframe_blind_spots():
    reflection = CognitiveReflection(
        reflection_summary=ReflectionSummary(),
        possible_blind_spots=["User ignores the emotional impact of the decision.", "User lacks understanding of basic physics."],
        confidence=0.8
    )
    
    result = reframe_blind_spots(reflection)
    
    # Assert harsh language is reframed to supportive language
    assert "ignores" not in result.possible_blind_spots[0]
    assert "has not yet explored" in result.possible_blind_spots[0]
    
    assert "lacks" not in result.possible_blind_spots[1]
    assert "might benefit from" in result.possible_blind_spots[1]

@pytest.mark.asyncio
async def test_reflection_llm_service():
    service = ReflectionLLMService()
    
    result = await service.process_reflection(
        raw_input="I am building a system architecture.",
        intent=None, mode=None, thought=None, memory=None
    )
    
    assert result.reflection_summary is not None
    assert "Systems Architecture" in result.reflection_summary.dominant_themes
    assert len(result.possible_blind_spots) > 0
