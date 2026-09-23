from enum import Enum

class AmbiguityType(str, Enum):
    MISSING_CONTEXT = "missing_context"
    UNDEFINED_GOAL = "undefined_goal"
    VAGUE_TERMINOLOGY = "vague_terminology"
    EMOTIONAL_AMBIGUITY = "emotional_ambiguity"
    CONCEPTUAL_UNCERTAINTY = "conceptual_uncertainty"
    EXPLORATORY_CURIOSITY = "exploratory_curiosity"
    CONTRADICTORY_INTENT = "contradictory_intent"
    UNDEFINED_SCOPE = "undefined_scope"
    INCOMPLETE_CONSTRAINTS = "incomplete_constraints"
    ABSTRACT_EXPRESSION = "abstract_expression"

class ClarificationDepth(str, Enum):
    LIGHT = "light"
    MEDIUM = "medium"
    DEEP = "deep"
    NONE = "none"
