import pytest
import asyncio
from src.schemas.cognitive import IntegrationState, ToolCall, IntegrationResult
from src.services.integration.taxonomy import ToolPermissionLevel
from src.services.integration.heuristics import (
    validate_permission_boundaries,
    sanitize_tool_parameters,
    enforce_rate_limits
)
from src.services.integration.engine import IntegrationLLMService

def test_validate_permission_boundaries():
    # Setup state with a HIGH permission tool call
    state = IntegrationState(
        tool_execution_plan=[
            ToolCall(
                tool_id="high_risk_tool",
                tool_name="Risk Tool",
                parameters={},
                permission_level_required=ToolPermissionLevel.HIGH.value
            )
        ],
        integration_results=[],
        workflow_status="executing",
        confidence=1.0
    )
    
    result = validate_permission_boundaries(state)
    
    # Assert it was flagged for approval
    assert result.workflow_status == "awaiting_approval"
    assert any(r.status == "pending_approval" for r in result.integration_results)

def test_sanitize_tool_parameters():
    state = IntegrationState(
        tool_execution_plan=[
            ToolCall(
                tool_id="api_tool",
                tool_name="API Tool",
                parameters={"api_key": "secret-123", "data": "safe"},
                permission_level_required="low"
            )
        ],
        integration_results=[],
        workflow_status="executing",
        confidence=1.0
    )
    
    result = sanitize_tool_parameters(state)
    
    # Assert sensitive key was redacted
    assert result.tool_execution_plan[0].parameters["api_key"] == "[REDACTED_BEFORE_EXECUTION]"
    assert result.tool_execution_plan[0].parameters["data"] == "safe"

def test_enforce_rate_limits():
    # 10 tools planned
    calls = [ToolCall(tool_id=f"t{i}", tool_name=f"T{i}", parameters={}, permission_level_required="low") for i in range(10)]
    state = IntegrationState(
        tool_execution_plan=calls,
        integration_results=[],
        workflow_status="executing",
        confidence=1.0
    )
    
    result = enforce_rate_limits(state)
    
    # Assert truncated to 5
    assert len(result.tool_execution_plan) == 5

@pytest.mark.asyncio
async def test_integration_llm_service():
    service = IntegrationLLMService()
    
    result = await service.plan_integration(
        raw_input="Schedule a focus session on my calendar",
        intent=None, research=None, collaboration=None
    )
    
    assert result.workflow_status == "awaiting_approval"
    assert result.tool_execution_plan[0].tool_id == "gcal_insert_v1"
    assert result.tool_execution_plan[0].permission_level_required == ToolPermissionLevel.HIGH.value
