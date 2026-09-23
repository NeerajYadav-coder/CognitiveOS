import pytest
import asyncio
from src.schemas.cognitive import CognitiveState, AmbiguityAnalysis, ClarificationStrategy, IntentExtraction
from src.services.orchestration.heuristics import should_skip_memory_and_reflection, route_next_engines

def test_high_ambiguity_skips_deep_engines():
    # Setup state with high ambiguity that requires clarification
    state = CognitiveState(
        session_id="test",
        raw_input="i don't know",
        ambiguity=AmbiguityAnalysis(
            ambiguity_score=0.9, ambiguity_type=["vagueness"], 
            clarification_strategy=ClarificationStrategy(enabled=True, question_count=1, depth="light", preserve_exploration=True),
            confidence=0.9
        )
    )
    
    assert should_skip_memory_and_reflection(state) is True
    
    decisions = route_next_engines(state, ["MemoryProfileEngine", "ReflectionEngine", "SemanticGraphEngine"])
    
    # Assert all deep engines were skipped
    for d in decisions:
        assert d.action == "skip"

def test_surface_intent_skips_semantic_graph():
    # Setup state with surface intent, shouldn't need a heavy graph
    state = CognitiveState(
        session_id="test",
        raw_input="fix my python script",
        intent=IntentExtraction(primary_intent="Debug", domain="Code", depth_level="surface", confidence=0.9)
    )
    
    decisions = route_next_engines(state, ["SemanticGraphEngine"])
    assert decisions[0].engine_name == "SemanticGraphEngine"
    assert decisions[0].action == "skip"
