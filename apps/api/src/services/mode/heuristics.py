import re
from typing import Dict, List
from src.schemas.cognitive import ModeScore
from src.services.mode.taxonomy import HEURISTIC_KEYWORDS, ModeRegistry

def generate_heuristic_baseline(raw_input: str) -> Dict[str, float]:
    """
    Scans the raw input for keyword markers to generate a baseline probability for each mode.
    This ensures that even if the LLM struggles with a highly ambiguous prompt, we have a statistical anchor.
    """
    input_lower = raw_input.lower()
    scores: Dict[str, float] = {mode.value: 0.0 for mode in ModeRegistry}
    
    # 1. Keyword Frequency Analysis
    for mode, keywords in HEURISTIC_KEYWORDS.items():
        match_count = sum(1 for kw in keywords if re.search(r'\b' + re.escape(kw) + r'\b', input_lower))
        # Diminishing returns on multiple keywords to prevent score blowup
        scores[mode.value] = min(0.6, match_count * 0.2)
        
    return scores

def merge_and_normalize_scores(llm_modes: List[ModeScore], baseline: Dict[str, float]) -> List[ModeScore]:
    """
    Blends the LLM probabilistic output with the heuristic baseline.
    Avoids overfitting by ensuring heuristic presence anchors the LLM.
    """
    merged = []
    
    for llm_mode in llm_modes:
        base_score = baseline.get(llm_mode.name.lower(), 0.0)
        # Weighting: 70% LLM contextual understanding, 30% heuristic anchoring
        blended_score = (llm_mode.score * 0.7) + (base_score * 0.3)
        merged.append(ModeScore(name=llm_mode.name.lower(), score=round(blended_score, 3)))
        
    # Sort descending
    merged.sort(key=lambda x: x.score, reverse=True)
    return merged

def determine_primary_mode(merged_modes: List[ModeScore]) -> str:
    """Safely extracts the primary mode, defaulting to exploratory if uncertain."""
    if not merged_modes:
        return ModeRegistry.EXPLORATORY.value
    return merged_modes[0].name
