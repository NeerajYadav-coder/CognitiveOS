from typing import List
from src.schemas.cognitive import CognitiveState, OrchestrationDecision

def should_skip_memory_and_reflection(state: CognitiveState) -> bool:
    """
    If ambiguity is extremely high and the clarification strategy is active,
    there is no coherent 'thought' yet to memorize or reflect upon.
    We should skip Memory, Reflection, and Graph to save compute and prevent junk data.
    """
    if state.ambiguity and state.ambiguity.clarification_strategy.enabled:
        return True
    return False

def requires_deep_semantic_graph(state: CognitiveState) -> bool:
    """
    If the user's cognitive depth preference is 'deep' or they are in 'philosophical' mode,
    the Semantic Graph engine is highly valuable.
    If it's just 'intermediate' or 'surface', it might be skipped to optimize latency.
    """
    if state.mode and "philosophical" in [m.name for m in state.mode.modes]:
        return True
    if state.intent and state.intent.depth_level in ["deep", "exploratory"]:
        return True
    return False

def route_next_engines(state: CognitiveState, remaining_engines: List[str]) -> List[OrchestrationDecision]:
    """
    Dynamically assesses the current cognitive state and decides what to do with the remaining engines.
    """
    decisions = []
    
    skip_deep_analysis = should_skip_memory_and_reflection(state)
    
    for engine_name in remaining_engines:
        if skip_deep_analysis and engine_name in ["MemoryProfileEngine", "ReflectionEngine", "SemanticGraphEngine"]:
            decisions.append(OrchestrationDecision(
                engine_name=engine_name,
                action="skip",
                reason="High ambiguity requires clarification before deep cognitive analysis."
            ))
        elif engine_name == "SemanticGraphEngine" and not requires_deep_semantic_graph(state):
            decisions.append(OrchestrationDecision(
                engine_name=engine_name,
                action="skip",
                reason="Semantic Graph skipped to optimize latency for surface-level intent."
            ))
        else:
            decisions.append(OrchestrationDecision(
                engine_name=engine_name,
                action="execute",
                reason="Default flow execution."
            ))
            
    return decisions
