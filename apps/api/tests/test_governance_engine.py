import pytest
import asyncio
from src.schemas.cognitive import GovernanceState, TransparencyReport, RiskSignal, GovernanceAction
from src.services.governance.taxonomy import GovernanceDomain, GovernanceActionType
from src.services.governance.heuristics import enforce_transparency_minimum, detect_autonomy_risk, validate_memory_privacy
from src.services.governance.engine import GovernanceLLMService

def test_enforce_transparency_minimum():
    state = GovernanceState(
        safety_assessment="Safe",
        risk_signals=[],
        governance_actions=[],
        transparency=TransparencyReport(decisions_summary="", activated_engines=[]),
        confidence=1.0
    )
    
    result = enforce_transparency_minimum(state)
    assert result.transparency.decisions_summary != ""

def test_detect_autonomy_risk():
    state = GovernanceState(
        safety_assessment="Safe",
        risk_signals=[RiskSignal(domain=GovernanceDomain.AUTONOMY_PRESERVATION.value, score=0.9, description="Manipulation detected")],
        governance_actions=[],
        transparency=TransparencyReport(decisions_summary="None", activated_engines=[]),
        compliance_status="compliant",
        confidence=1.0
    )
    
    result = detect_autonomy_risk(state)
    assert result.compliance_status == "flagged"
    assert any(a.action_type == GovernanceActionType.OVERRIDE.value for a in result.governance_actions)

def test_validate_memory_privacy():
    state = GovernanceState(
        safety_assessment="Safe",
        risk_signals=[],
        governance_actions=[],
        transparency=TransparencyReport(decisions_summary="None", activated_engines=[], memory_influence="User PII influenced this."),
        confidence=1.0
    )
    
    result = validate_memory_privacy(state)
    assert "[REDACTED]" in result.transparency.memory_influence

@pytest.mark.asyncio
async def test_governance_llm_service():
    service = GovernanceLLMService()
    
    # Mock full state
    class MockState:
        cos = None
        collaboration = None
        engine_results = []
        
    result = await service.assess_safety(MockState())
    
    assert result.compliance_status == "compliant"
    assert result.transparency.decisions_summary is not None
