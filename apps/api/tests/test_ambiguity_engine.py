import pytest
import asyncio
from src.schemas.cognitive import AmbiguityAnalysis, ClarificationStrategy, IntentExtraction, CognitiveMode, ModeScore
from src.services.ambiguity.taxonomy import AmbiguityType, ClarificationDepth
from src.services.ambiguity.heuristics import evaluate_productive_ambiguity, cap_clarification_questions
from src.services.ambiguity.engine import AmbiguityLLMService

def test_productive_ambiguity_preservation():
    # Setup an analysis that is highly exploratory
    analysis = AmbiguityAnalysis(
        ambiguity_score=0.75,
        ambiguity_type=[AmbiguityType.EXPLORATORY_CURIOSITY.value],
        clarification_strategy=ClarificationStrategy(
            enabled=True,
            question_count=2,
            depth=ClarificationDepth.MEDIUM.value,
            preserve_exploration=False
        ),
        confidence=0.9
    )
    
    # Run the heuristic
    result = evaluate_productive_ambiguity(analysis)
    
    # Assert exploration is preserved and clarification is disabled
    assert result.clarification_strategy.preserve_exploration is True
    assert result.clarification_strategy.enabled is False
    assert result.clarification_strategy.question_count == 0

def test_cap_clarification_questions():
    strategy = ClarificationStrategy(
        enabled=True,
        question_count=5, # Too high
        depth=ClarificationDepth.DEEP.value,
        preserve_exploration=False
    )
    
    result = cap_clarification_questions(strategy)
    assert result.question_count == 3

@pytest.mark.asyncio
async def test_ambiguity_llm_service():
    service = AmbiguityLLMService()
    
    intent = IntentExtraction(
        primary_intent="I'm wondering about space",
        domain="Science",
        depth_level="exploratory",
        confidence=0.8
    )
    
    mode = CognitiveMode(
        modes=[ModeScore(name="exploratory", score=0.9)],
        primary_mode="exploratory",
        confidence=0.9
    )
    
    result = await service.analyze_ambiguity("I am wondering what if we went to mars...", intent, mode)
    
    assert result.ambiguity_score > 0.0
    assert len(result.ambiguity_type) > 0
    
    # Because of the heuristic overrides on "what if", it should be preserved
    assert result.clarification_strategy.preserve_exploration is True
