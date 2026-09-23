import pytest
import asyncio
from src.schemas.cognitive import CognitiveOSState, WorkspaceState, StrategicFocus
from src.services.cos.taxonomy import EnvironmentStatus
from src.services.cos.heuristics import enforce_human_agency, detect_strategic_drift
from src.services.cos.engine import CognitiveOSLLMService

def test_enforce_human_agency():
    # Setup state with manipulative language
    state = CognitiveOSState(
        environment_state=WorkspaceState(
            active_exploration_domains=[],
            strategic_focus_areas=[],
            environment_status="idle"
        ),
        adaptive_assistance_note="You must focus on this right now.",
        confidence=1.0
    )
    
    result = enforce_human_agency(state)
    
    # Assert redaction
    assert "You might consider" in result.adaptive_assistance_note
    assert "You must" not in result.adaptive_assistance_note

def test_detect_strategic_drift():
    # Focused status but domain drift
    state = CognitiveOSState(
        environment_state=WorkspaceState(
            active_exploration_domains=["Deep Sea Diving"],
            strategic_focus_areas=[StrategicFocus(area="AI Coding", priority=1.0, current_objective="Write tests")],
            environment_status=EnvironmentStatus.FOCUSED.value
        ),
        confidence=1.0
    )
    
    result = detect_strategic_drift(state)
    
    # Assert shift to exploratory
    assert result.environment_state.environment_status == EnvironmentStatus.EXPLORATORY.value
    assert "diverged" in result.adaptive_assistance_note

@pytest.mark.asyncio
async def test_cos_llm_service():
    service = CognitiveOSLLMService()
    
    result = await service.manage_environment(
        raw_input="Let's reflect on my progress.",
        intent=None, memory=None, reflection=None, graph=None
    )
    
    assert result.sync_status == "synchronized"
    assert result.environment_state is not None
    assert result.adaptive_assistance_note is not None
