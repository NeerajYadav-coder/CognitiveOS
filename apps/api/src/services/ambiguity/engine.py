import asyncio
from typing import Optional

from src.schemas.cognitive import AmbiguityAnalysis, ClarificationStrategy, IntentExtraction, CognitiveMode
from src.services.ambiguity.taxonomy import AmbiguityType, ClarificationDepth
from src.services.ambiguity.heuristics import evaluate_productive_ambiguity, cap_clarification_questions
from src.utils.logger import logger

class AmbiguityLLMService:
    """
    Abstracts LLM communication for Cognitive Ambiguity Analysis.
    Determines if clarification is needed or if ambiguity should be preserved.
    """
    
    async def analyze_ambiguity(
        self, 
        raw_input: str, 
        intent: Optional[IntentExtraction], 
        mode: Optional[CognitiveMode]
    ) -> AmbiguityAnalysis:
        
        logger.debug("Calling LLM for Ambiguity Analysis...")
        
        # Simulate LLM Network Call
        await asyncio.sleep(0.3)
        
        raw_lower = raw_input.lower()
        ambiguity_types = []
        score = 0.5
        
        # Mocking deterministic classification based on input heuristics
        if len(raw_input.split()) < 4:
            ambiguity_types.append(AmbiguityType.MISSING_CONTEXT.value)
            score = 0.9
        
        if "wondering" in raw_lower or "what if" in raw_lower or "maybe" in raw_lower:
            ambiguity_types.append(AmbiguityType.EXPLORATORY_CURIOSITY.value)
            score = 0.7
            
        if "but also" in raw_lower or "however" in raw_lower:
            ambiguity_types.append(AmbiguityType.CONTRADICTORY_INTENT.value)
            score = 0.85
            
        if not ambiguity_types:
            ambiguity_types.append(AmbiguityType.VAGUE_TERMINOLOGY.value)
            score = 0.3
            
        # Initial Raw LLM Output Mock
        analysis = AmbiguityAnalysis(
            ambiguity_score=score,
            ambiguity_type=ambiguity_types,
            clarification_strategy=ClarificationStrategy(
                enabled=score > 0.6,
                question_count=2 if score > 0.8 else 1,
                depth=ClarificationDepth.MEDIUM.value if score > 0.8 else ClarificationDepth.LIGHT.value,
                preserve_exploration=False
            ),
            confidence=0.88
        )
        
        # 1. Apply Productive Ambiguity Heuristic overrides
        analysis = evaluate_productive_ambiguity(analysis)
        
        # 2. Apply Boundary Restrictions
        analysis.clarification_strategy = cap_clarification_questions(analysis.clarification_strategy)
        
        return analysis
