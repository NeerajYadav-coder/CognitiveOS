import pytest
import asyncio
from src.schemas.cognitive import CognitiveMemory, CognitiveProfileUpdates, MemoryEvent
from src.services.memory.taxonomy import MemoryCategory
from src.services.memory.heuristics import enforce_privacy_boundaries, prevent_cognitive_overfitting
from src.services.memory.engine import MemoryLLMService

def test_privacy_boundary_enforcement():
    # Setup a memory event containing sensitive PII
    memory = CognitiveMemory(
        cognitive_profile_updates=CognitiveProfileUpdates(
            dominant_modes=["technical"], recurring_domains=["software"], depth_preference="deep", reasoning_style="analytical"
        ),
        memory_events=[
            MemoryEvent(category=MemoryCategory.RECURRING_THEME.value, content="User email is user@example.com and phone is 555-123-4567.", temporal_weight=1.0)
        ],
        confidence=0.9
    )
    
    result = enforce_privacy_boundaries(memory)
    
    # Assert PII is redacted
    content = result.memory_events[0].content
    assert "user@example.com" not in content
    assert "555-123-4567" not in content
    assert "[REDACTED]" in content

@pytest.mark.asyncio
async def test_memory_llm_service():
    service = MemoryLLMService()
    
    result = await service.process_memory(
        raw_input="I am feeling disconnected from society.",
        intent=None, mode=None, thought=None
    )
    
    assert result.cognitive_profile_updates is not None
    assert "philosophical" in result.cognitive_profile_updates.dominant_modes
    assert len(result.memory_events) > 0
    assert result.memory_events[0].category == MemoryCategory.CONCEPTUAL_INTEREST.value
