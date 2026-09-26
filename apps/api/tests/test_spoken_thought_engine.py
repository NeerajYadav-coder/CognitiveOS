import pytest
import asyncio
from src.services.spoken_thought.engine import (
    clean_verbal_fillers,
    calculate_spoken_ambiguity,
    SpokenThoughtEngine
)
from src.schemas.cognitive import SpokenThoughtAnalysis

def test_clean_verbal_fillers():
    raw = "Um, so basically, I am thinking about, you know, how the the brain works, right?"
    cleaned, fillers = clean_verbal_fillers(raw)
    
    assert "um" in [f.lower() for f in fillers]
    assert "you know" in [f.lower() for f in fillers]
    assert "basically" in [f.lower() for f in fillers]
    assert "the the" not in cleaned
    assert "how the brain works" in cleaned

def test_spoken_ambiguity_scoring():
    clear_speech = "We need to optimize the database query latency using indexed views."
    cleaned_clear, fillers_clear = clean_verbal_fillers(clear_speech)
    score_clear = calculate_spoken_ambiguity(clear_speech, cleaned_clear, len(fillers_clear))
    
    vague_speech = "Um, like, maybe we should do something with the stuff, I dunno, whatever."
    cleaned_vague, fillers_vague = clean_verbal_fillers(vague_speech)
    score_vague = calculate_spoken_ambiguity(vague_speech, cleaned_vague, len(fillers_vague))
    
    assert score_vague > score_clear
    assert 0.0 <= score_clear <= 1.0
    assert 0.0 <= score_vague <= 1.0

@pytest.mark.asyncio
async def test_spoken_thought_engine_process_fallback():
    engine = SpokenThoughtEngine(client=None)
    raw = "So yeah, I want to build something that connects ant colonies and microservices architecture."
    
    result = await engine.process(raw)
    
    assert isinstance(result, SpokenThoughtAnalysis)
    assert len(result.cleaned_transcript) > 0
    assert len(result.latent_hypotheses) > 0
    assert len(result.focal_question) > 0
    assert len(result.suggested_prompt) > 0
    assert 0.0 <= result.spoken_ambiguity_score <= 1.0
