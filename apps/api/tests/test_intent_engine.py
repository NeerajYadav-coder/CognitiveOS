import pytest
import asyncio
from unittest.mock import AsyncMock, patch
import json

from src.schemas.cognitive import IntentExtraction
from src.services.intent.scoring import calculate_confidence, validate_intent
from src.services.intent.engine import IntentLLMService

def test_confidence_scoring_heuristics():
    intent = IntentExtraction(
        primary_intent="Learn Python",
        secondary_intents=["Understand async"],
        domain="Programming",
        depth_level="surface",
        confidence=1.0
    )
    raw_input = "I want to learn python so I can write async code."
    
    score = calculate_confidence(raw_input, intent)
    assert score > 0.7

def test_low_confidence_on_vague_extraction():
    intent = IntentExtraction(
        primary_intent="do thing",
        secondary_intents=[],
        domain="unknown",
        depth_level="surface",
        confidence=1.0
    )
    raw_input = "help"
    
    score = calculate_confidence(raw_input, intent)
    assert score < 0.6
    
    intent.confidence = score
    assert not validate_intent(intent)

@pytest.mark.asyncio
async def test_intent_llm_service():
    mock_choice = AsyncMock()
    mock_choice.message.content = json.dumps({
        "primary_intent": "Understanding core concepts and mechanisms.",
        "secondary_intents": ["Identify root cause"],
        "domain": "Science",
        "depth_level": "first_principles",
        "confidence": 0.95
    })
    mock_response = AsyncMock()
    mock_response.choices = [mock_choice]
    
    with patch("openai.resources.chat.completions.AsyncCompletions.create", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_response
        service = IntentLLMService()
        result = await service.extract_intent("Why is the sky blue?")
        
        assert isinstance(result, IntentExtraction)
        assert result.depth_level == "first_principles"
        assert result.confidence > 0.0
