import pytest
import asyncio
from unittest.mock import AsyncMock, patch
import json

from src.schemas.cognitive import IntentExtraction, ModeScore
from src.services.mode.heuristics import generate_heuristic_baseline, merge_and_normalize_scores
from src.services.mode.engine import ModeLLMService

def test_heuristic_keyword_baseline_mixed():
    # A prompt that mixes technical language and emotional language
    raw = "I am so frustrated because this database compile error keeps happening."
    scores = generate_heuristic_baseline(raw)
    
    assert scores["technical"] > 0.0
    assert scores["emotional"] > 0.0
    # Should not score highly on philosophical
    assert scores["philosophical"] == 0.0

def test_merge_scores_weights():
    baseline = {"technical": 0.5, "philosophical": 0.0}
    llm_output = [
        ModeScore(name="technical", score=0.8),
        ModeScore(name="philosophical", score=0.9)
    ]
    
    merged = merge_and_normalize_scores(llm_output, baseline)
    
    # technical: (0.8 * 0.7) + (0.5 * 0.3) = 0.56 + 0.15 = 0.71
    # philosophical: (0.9 * 0.7) + (0.0 * 0.3) = 0.63
    
    assert merged[0].name == "technical"
    assert merged[0].score > merged[1].score

@pytest.mark.asyncio
async def test_mode_llm_service():
    mock_choice = AsyncMock()
    mock_choice.message.content = json.dumps({
        "modes": [
            {"name": "technical", "score": 0.95},
            {"name": "philosophical", "score": 0.1}
        ],
        "primary_mode": "technical",
        "confidence": 0.95
    })
    mock_response = AsyncMock()
    mock_response.choices = [mock_choice]
    
    with patch("openai.resources.chat.completions.AsyncCompletions.create", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_response
        service = ModeLLMService()
        intent = IntentExtraction(
            primary_intent="Understand why the bug happens",
            domain="Software",
            depth_level="surface",
            confidence=0.9
        )
        result = await service.detect_mode("Why does this bug happen?", intent)
        
        assert len(result.modes) > 0
        assert result.primary_mode is not None
        assert result.confidence > 0.0
