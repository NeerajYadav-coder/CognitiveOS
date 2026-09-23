import pytest
import asyncio
from unittest.mock import AsyncMock, patch
import json

from src.schemas.cognitive import ThoughtStructure, StructuredThought
from src.services.structuring.taxonomy import ThinkingStructureType
from src.services.structuring.heuristics import enforce_exploratory_preservation
from src.services.structuring.engine import StructuringLLMService

def test_exploratory_preservation_heuristic():
    # Setup a thought that is exploratory but the LLM forced problem-solving wording
    thought = ThoughtStructure(
        structured_thought=StructuredThought(
            core_question="How to fix the universe?",
            exploration_direction="Mapping abstract concepts",
            subtopics=["Space", "Time"],
            missing_context=[],
            possible_domains=["Physics"],
            thinking_structure=ThinkingStructureType.EXPLORATORY.value
        ),
        clarified_representation="I want to know how to fix the universe.",
        confidence=0.8
    )
    
    result = enforce_exploratory_preservation(thought)
    
    # Assert the wording was softened to preserve exploration
    assert "Exploring the nature" in result.structured_thought.core_question
    assert result.structured_thought.thinking_structure == ThinkingStructureType.EXPLORATORY.value

@pytest.mark.asyncio
async def test_structuring_llm_service():
    mock_choice = AsyncMock()
    mock_choice.message.content = json.dumps({
        "structured_thought": {
            "core_question": "What is the root cause and meaning behind the feeling of societal disconnection?",
            "exploration_direction": "Philosophical and psychological exploration of identity and community.",
            "subtopics": ["Existential alienation", "Modern social structures", "Individual purpose"],
            "missing_context": [],
            "possible_domains": ["philosophy"],
            "thinking_structure": ThinkingStructureType.PHILOSOPHICAL.value
        },
        "clarified_representation": "I am experiencing a profound sense of disconnection from society and want to explore the philosophical and psychological roots of this alienation.",
        "confidence": 0.89
    })
    mock_response = AsyncMock()
    mock_response.choices = [mock_choice]
    
    with patch("openai.resources.chat.completions.AsyncCompletions.create", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_response
        
        service = StructuringLLMService()
        result = await service.structure_thought(
            raw_input="I just feel completely disconnected from society and alone",
            intent=None, mode=None, ambiguity=None, vocabulary=None
        )
        
        assert result.structured_thought.thinking_structure == ThinkingStructureType.PHILOSOPHICAL.value
        assert len(result.structured_thought.subtopics) > 0
        assert result.clarified_representation is not None
