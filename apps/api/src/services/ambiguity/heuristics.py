from src.schemas.cognitive import AmbiguityAnalysis, ClarificationStrategy
from src.services.ambiguity.taxonomy import AmbiguityType, ClarificationDepth

def evaluate_productive_ambiguity(analysis: AmbiguityAnalysis) -> AmbiguityAnalysis:
    """
    Heuristic rule to prevent over-questioning.
    If the primary ambiguity is exploratory or conceptual, we preserve it.
    """
    productive_types = [
        AmbiguityType.EXPLORATORY_CURIOSITY.value,
        AmbiguityType.ABSTRACT_EXPRESSION.value
    ]
    
    is_productive = any(t in analysis.ambiguity_type for t in productive_types)
    
    if is_productive and analysis.ambiguity_score < 0.8:
        # It's vague but intentionally so. Do not force clarification.
        analysis.clarification_strategy.enabled = False
        analysis.clarification_strategy.depth = ClarificationDepth.NONE.value
        analysis.clarification_strategy.preserve_exploration = True
        analysis.clarification_strategy.question_count = 0
        
    return analysis

def cap_clarification_questions(strategy: ClarificationStrategy) -> ClarificationStrategy:
    """
    Safety boundary: Never ask more than 3 questions at once to prevent user fatigue.
    """
    if strategy.enabled and strategy.question_count > 3:
        strategy.question_count = 3
    return strategy
