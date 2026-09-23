from enum import Enum
from typing import Dict, List

class ModeRegistry(str, Enum):
    TECHNICAL = "technical"
    RESEARCH = "research"
    PHILOSOPHICAL = "philosophical"
    CREATIVE = "creative"
    EMOTIONAL = "emotional"
    PRACTICAL = "practical"
    STRATEGIC = "strategic"
    EXPLORATORY = "exploratory"
    EDUCATIONAL = "educational"
    DEBATE = "debate"

# Keyword maps for heuristic baseline scoring
HEURISTIC_KEYWORDS: Dict[ModeRegistry, List[str]] = {
    ModeRegistry.TECHNICAL: ["code", "architecture", "api", "database", "system", "deploy", "compile", "error", "bug"],
    ModeRegistry.RESEARCH: ["find", "source", "evidence", "study", "data", "history", "who", "when", "literature"],
    ModeRegistry.PHILOSOPHICAL: ["meaning", "purpose", "why", "exist", "consciousness", "ethics", "morality", "truth"],
    ModeRegistry.CREATIVE: ["imagine", "story", "poem", "design", "art", "novel", "brainstorm", "concept"],
    ModeRegistry.EMOTIONAL: ["feel", "frustrated", "happy", "sad", "overwhelmed", "angry", "love", "hate"],
    ModeRegistry.PRACTICAL: ["how to", "step by step", "guide", "tutorial", "fix", "repair", "build", "recipe"],
    ModeRegistry.STRATEGIC: ["plan", "goal", "roadmap", "future", "optimize", "growth", "business", "scale"],
    ModeRegistry.EXPLORATORY: ["what if", "maybe", "curious", "wondering", "possibility", "explore", "idea"],
    ModeRegistry.EDUCATIONAL: ["learn", "explain", "understand", "teach", "beginner", "concept", "lesson"],
    ModeRegistry.DEBATE: ["versus", "vs", "compare", "pros and cons", "argument", "better", "disagree"]
}
