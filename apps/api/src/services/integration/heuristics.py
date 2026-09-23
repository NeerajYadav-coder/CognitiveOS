from src.schemas.cognitive import IntegrationState, ToolCall, IntegrationResult
from src.services.integration.taxonomy import ToolPermissionLevel

def validate_permission_boundaries(state: IntegrationState) -> IntegrationState:
    """
    Ensures that any tool call with HIGH or CRITICAL permission levels is 
    automatically flagged for approval and restricted in the immediate execution plan.
    """
    for call in state.tool_execution_plan:
        if call.permission_level_required in [ToolPermissionLevel.HIGH.value, ToolPermissionLevel.CRITICAL.value]:
            # Inject a pending approval result if not already present
            if not any(r.tool_id == call.tool_id for r in state.integration_results):
                state.integration_results.append(IntegrationResult(
                    tool_id=call.tool_id,
                    status="pending_approval",
                    execution_time_ms=0.0
                ))
            state.workflow_status = "awaiting_approval"
            
    return state

def sanitize_tool_parameters(state: IntegrationState) -> IntegrationState:
    """
    Scans tool parameters for potentially malicious patterns or sensitive data leaks
    before they are passed to the execution environment.
    """
    sensitive_keys = ["password", "token", "secret", "key", "auth"]
    for call in state.tool_execution_plan:
        for key in list(call.parameters.keys()):
            if any(sk in key.lower() for sk in sensitive_keys):
                call.parameters[key] = "[REDACTED_BEFORE_EXECUTION]"
                
    return state

def enforce_rate_limits(state: IntegrationState) -> IntegrationState:
    """
    Prevents tool execution explosions by capping the number of tool calls 
    per cognitive session.
    """
    MAX_TOOLS = 5
    if len(state.tool_execution_plan) > MAX_TOOLS:
        state.tool_execution_plan = state.tool_execution_plan[:MAX_TOOLS]
        # In a real system, we would log this truncation for audit.
        
    return state
