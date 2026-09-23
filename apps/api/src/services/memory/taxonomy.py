from enum import Enum

class MemoryCategory(str, Enum):
    RECURRING_THEME = "recurring_intellectual_theme"
    PREFERRED_MODE = "preferred_cognitive_mode"
    CURIOSITY_DOMAIN = "curiosity_domain"
    EXPLORATION_PATTERN = "exploration_pattern"
    REASONING_PREFERENCE = "reasoning_preference"
    DEPTH_PREFERENCE = "depth_preference"
    COMMUNICATION_PREFERENCE = "communication_preference"
    CONCEPTUAL_INTEREST = "conceptual_interest"
    INTERACTION_TENDENCY = "interaction_tendency"
    LONG_TERM_TRAJECTORY = "long_term_trajectory"
