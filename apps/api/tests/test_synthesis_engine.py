import pytest
import asyncio
from src.schemas.cognitive import PromptSynthesis, PromptStructure, ClarificationStrategy
from src.services.synthesis.heuristics import inject_clarification_constraints, validate_exploratory_formatting
from src.services.synthesis.engine import SynthesisLLMService

def test_inject_clarification_constraints():
    # Simulate a synthesis output
    synthesis = PromptSynthesis(
        final_prompt="Here is my question to the LLM.",
        prompt_structure=PromptStructure(
            context="Testing context", objective="Answer me", depth_level="surface", reasoning_style="analytical"
        ),
        confidence=0.9
    )
    
    # Simulate an ambiguity state requiring clarification
    strategy = ClarificationStrategy(enabled=True, question_count=2, depth="deep", preserve_exploration=False)
    
    result = inject_clarification_constraints(synthesis, strategy)
    
    # Assert constraint was injected
    assert "BEFORE answering" in result.final_prompt
    assert any("2 clarifying questions" in c for c in result.prompt_structure.constraints)
    assert len(result.optimization_notes) > 0

def test_exploratory_formatting_validation():
    # Simulate a prompt that is exploratory but the LLM forced rigid constraints
    synthesis = PromptSynthesis(
        final_prompt="...",
        prompt_structure=PromptStructure(
            context="...", objective="...", depth_level="exploratory", reasoning_style="Socratic exploration",
            constraints=["You must output JSON strictly", "Follow a strict format"]
        ),
        confidence=0.8
    )
    
    result = validate_exploratory_formatting(synthesis)
    
    # Assert rigid constraints were stripped
    assert len(result.prompt_structure.constraints) == 0

from unittest.mock import AsyncMock, patch
import json

@pytest.mark.asyncio
async def test_synthesis_llm_service():
    mock_choice = AsyncMock()
    mock_choice.message.content = json.dumps({
        "final_prompt": "Context: The user is experiencing feeling disconnected and alone.",
        "prompt_structure": {
            "context": "Expert Synthesis",
            "objective": "High-order prompt generation",
            "constraints": ["Do not offer medical advice"],
            "depth_level": "deep",
            "reasoning_style": "Architectural"
        }
    })
    
    mock_response = AsyncMock()
    mock_response.choices = [mock_choice]
    
    with patch("openai.resources.chat.completions.AsyncCompletions.create", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_response
        service = SynthesisLLMService()
        result = await service.synthesize_prompt(
            raw_input="I am feeling disconnected and alone.",
            intent=None, mode=None, ambiguity=None, vocabulary=None, thought=None
        )
        
        assert "Context: The user is experiencing" in result.final_prompt
        assert "Do not offer medical advice" in result.prompt_structure.constraints
