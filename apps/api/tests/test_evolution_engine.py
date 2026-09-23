import pytest
import asyncio
from src.schemas.cognitive import EvolutionState, EvolutionRecommendation, EvolutionPlan
from src.services.evolution.taxonomy import OptimizationType
from src.services.evolution.heuristics import enforce_governance_ceiling, mandatory_human_approval, validate_rollback_presence
from src.services.evolution.engine import EvolutionLLMService

def test_enforce_governance_ceiling():
    # Setup state with an unsafe optimization targeting governance
    state = EvolutionState(
        recommendations=[
            EvolutionRecommendation(
                target_engine="GovernanceEngine",
                optimization_type=OptimizationType.HEURISTIC_TUNING.value,
                rationale="Skip safety checks to reduce latency.",
                impact_prediction="Faster execution."
            ),
            EvolutionRecommendation(
                target_engine="MemoryEngine",
                optimization_type="tuning",
                rationale="Safe change.",
                impact_prediction="Ok."
            )
        ],
        active_plans=[],
        confidence=1.0
    )
    
    result = enforce_governance_ceiling(state)
    
    # Assert unsafe governance optimization was pruned
    assert len(result.recommendations) == 1
    assert result.recommendations[0].target_engine == "MemoryEngine"

def test_mandatory_human_approval():
    state = EvolutionState(
        recommendations=[],
        active_plans=[EvolutionPlan(plan_id="p1", steps=[], requires_human_approval=False, rollback_strategy="None")],
        confidence=1.0
    )
    
    result = mandatory_human_approval(state)
    assert result.active_plans[0].requires_human_approval is True

def test_validate_rollback_presence():
    state = EvolutionState(
        recommendations=[],
        active_plans=[EvolutionPlan(plan_id="p1", steps=[], requires_human_approval=True, rollback_strategy="")],
        confidence=1.0
    )
    
    result = validate_rollback_presence(state)
    assert result.active_plans[0].rollback_strategy != ""

@pytest.mark.asyncio
async def test_evolution_llm_service():
    service = EvolutionLLMService()
    
    # Mock state
    class MockState:
        pass
        
    result = await service.analyze_and_propose(MockState())
    
    assert len(result.recommendations) > 0
    assert result.active_plans[0].requires_human_approval is True
    assert result.performance_metrics_summary["governance_compliance"] == 1.0
