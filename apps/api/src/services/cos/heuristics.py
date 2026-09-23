from src.schemas.cognitive import CognitiveOSState, WorkspaceState
from src.services.cos.taxonomy import EnvironmentStatus

import re

def enforce_human_agency(state: CognitiveOSState) -> CognitiveOSState:
    """
    Ensures that adaptive assistance notes never use manipulative or 
    authoritarian language. They must remain suggestive and assistive.
    """
    if state.adaptive_assistance_note:
        manipulative_patterns = ["you must", "you should only", "the only way", "stop thinking"]
        for pattern in manipulative_patterns:
            def replace_case(match):
                text = match.group(0)
                if text and text[0].isupper():
                    return "You might consider"
                return "you might consider"
            state.adaptive_assistance_note = re.sub(
                re.escape(pattern), replace_case, state.adaptive_assistance_note, flags=re.IGNORECASE
            )
                
    return state

def detect_strategic_drift(state: CognitiveOSState) -> CognitiveOSState:
    """
    If the current exploration domains are completely disconnected from the 
    defined strategic focus areas, we flag this as 'exploratory' mode 
    to preserve the user's intellectual continuity without forcing them back.
    """
    env = state.environment_state
    if len(env.strategic_focus_areas) > 0 and len(env.active_exploration_domains) > 0:
        # Check for overlap (simulated with string matches for now)
        has_overlap = any(
            domain.lower() in area.area.lower() 
            for domain in env.active_exploration_domains 
            for area in env.strategic_focus_areas
        )
        
        if not has_overlap and env.environment_status == EnvironmentStatus.FOCUSED.value:
            env.environment_status = EnvironmentStatus.EXPLORATORY.value
            state.adaptive_assistance_note = "I've shifted your workspace to Exploratory mode as your current inquiry has diverged from your primary strategic focus."
            
    return state
