import re
from typing import List
from src.schemas.cognitive import IntentExtraction

def calculate_confidence(raw_input: str, parsed_intent: IntentExtraction) -> float:
    """
    Calculates a heuristic confidence score based on the extracted intent vs raw input.
    - Penalizes empty domains.
    - Rewards specificity in primary_intent.
    - Adjusts based on length of input vs length of extraction.
    """
    base_confidence = 0.8  # Start with high confidence if LLM returned valid JSON
    
    # Heuristics
    if not parsed_intent.primary_intent or len(parsed_intent.primary_intent) < 5:
        base_confidence -= 0.3
        
    if parsed_intent.domain.lower() in ["unknown", "general", "n/a"]:
        base_confidence -= 0.20
        
    if not parsed_intent.secondary_intents:
        # Lacking secondary intents might just mean simple prompt, slight penalty
        base_confidence -= 0.05
        
    # Check for exact hallucinated phrases (if the intent is longer than the raw input by a huge margin)
    if len(parsed_intent.primary_intent) > len(raw_input) * 2 and len(raw_input) > 20:
        base_confidence -= 0.2
        
    return max(0.0, min(1.0, base_confidence))

def validate_intent(intent: IntentExtraction) -> bool:
    """Validates edge case integrity for extracted intent."""
    if intent.confidence < 0.6:
        return False
    return True
