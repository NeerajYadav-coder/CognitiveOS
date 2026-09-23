import pytest
import asyncio
from unittest.mock import AsyncMock, patch
import json

from src.schemas.cognitive import VocabularyExpansion, SemanticExpansion
from src.services.vocabulary.heuristics import filter_hallucinated_terms
from src.services.vocabulary.engine import VocabularyLLMService

def test_filter_hallucinated_terms():
    # Setup an expansion where the LLM hallucinated a weird low-confidence term
    expansion = VocabularyExpansion(
        core_expression="feeling alone",
        semantic_expansions=[
            SemanticExpansion(term="existential alienation", confidence=0.9, domain="philosophy"),
            SemanticExpansion(term="quantum entanglement", confidence=0.2, domain="physics") # Hallucination
        ],
        adjacent_concepts=["isolation"],
        recommended_terms=["existential alienation", "quantum entanglement"]
    )
    
    result = filter_hallucinated_terms(expansion)
    
    # Assert the low confidence term was stripped
    assert len(result.semantic_expansions) == 1
    assert result.semantic_expansions[0].term == "existential alienation"
    assert "quantum entanglement" not in result.recommended_terms
    assert "existential alienation" in result.recommended_terms

@pytest.mark.asyncio
async def test_vocabulary_llm_service():
    mock_choice = AsyncMock()
    mock_choice.message.content = json.dumps({
        "core_expression": "feeling disconnected from society",
        "semantic_expansions": [
            {"term": "existential alienation", "confidence": 0.88, "domain": "philosophy"},
            {"term": "social detachment", "confidence": 0.74, "domain": "psychology"},
            {"term": "anomie", "confidence": 0.6, "domain": "sociology"}
        ],
        "adjacent_concepts": ["identity crisis", "meaning", "isolation"],
        "recommended_terms": ["existential alienation", "social detachment"]
    })
    mock_response = AsyncMock()
    mock_response.choices = [mock_choice]
    
    with patch("openai.resources.chat.completions.AsyncCompletions.create", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_response
        
        service = VocabularyLLMService()
        result = await service.expand_vocabulary(
            raw_input="I just feel completely disconnected from society and alone",
            intent=None, mode=None, ambiguity=None
        )
        
        assert "feeling disconnected" in result.core_expression.lower()
        assert len(result.semantic_expansions) > 0
        assert result.semantic_expansions[0].domain == "philosophy"
        assert len(result.adjacent_concepts) > 0
        
        # Assert the low confidence 'anomie' was stripped out by filter_hallucinated_terms
        assert not any(e.term == "anomie" for e in result.semantic_expansions)
