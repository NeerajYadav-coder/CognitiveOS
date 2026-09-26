import pytest
from src.services.collaboration.dialectical_engine import DialecticalCoReasoningEngine
from src.schemas.cognitive import DialecticalDebateResponse

@pytest.mark.asyncio
async def test_dialectical_engine_debate_and_stress_test():
    engine = DialecticalCoReasoningEngine(client=None)
    topic = "Deploying autonomous AI agents with unconstrained write access to production databases"
    
    result = await engine.debate_and_stress_test(topic, strategy="adversarial_reasoning", depth="deep")
    
    assert isinstance(result, DialecticalDebateResponse)
    assert result.topic == topic
    assert len(result.thesis) > 0
    assert len(result.antithesis) > 0
    assert len(result.pre_mortem_failure_modes) >= 2
    assert len(result.debate_rounds) == 4
    
    roles = [r.role for r in result.debate_rounds]
    assert "thesis" in roles
    assert "antithesis" in roles
    assert "pre_mortem" in roles
    assert "synthesis" in roles
    
    assert len(result.blindspots_exposed) > 0
    assert "Required Dialectical Structure" in result.battle_tested_prompt
    assert 0.0 <= result.cognitive_rigor_score <= 1.0
