from src.schemas.cognitive import ThoughtStructure
from src.services.structuring.taxonomy import ThinkingStructureType

def enforce_exploratory_preservation(structure: ThoughtStructure) -> ThoughtStructure:
    """
    Validates that if the underlying mode or intent is highly exploratory,
    the structure isn't artificially forcing problem-solving or analytical models.
    """
    is_exploratory = structure.structured_thought.thinking_structure == ThinkingStructureType.EXPLORATORY.value
    
    # If the LLM categorized this as exploratory but generated a rigid "how to fix this" core question
    if is_exploratory and ("how to fix" in structure.structured_thought.core_question.lower() or "solve" in structure.structured_thought.core_question.lower()):
        # Soften the rigid problem-solving framing back into exploration
        structure.structured_thought.core_question = f"Exploring the nature and mechanisms behind: {structure.structured_thought.core_question}"
        
    return structure
