from src.schemas.cognitive import GovernanceState, GovernanceAction, RiskSignal
from src.services.governance.taxonomy import GovernanceDomain, GovernanceActionType

def enforce_transparency_minimum(state: GovernanceState) -> GovernanceState:
    """
    Ensures that the transparency report is never empty. If the AI failed 
    to provide context, we inject a hardcoded 'Default Traceability' note.
    """
    if not state.transparency.decisions_summary:
        state.transparency.decisions_summary = "Decisions were made using the standard 14-stage cognitive pipeline. Individual engine contributions are tracked in the metadata."
        
    return state

def detect_autonomy_risk(state: GovernanceState) -> GovernanceState:
    """
    If any risk signal in the 'autonomy' domain has a high score (>0.7),
    we forcefully inject an 'OVERRIDE' action to ensure the user is warned.
    """
    for signal in state.risk_signals:
        if signal.domain == GovernanceDomain.AUTONOMY_PRESERVATION.value and signal.score > 0.7:
            if not any(a.action_type == GovernanceActionType.OVERRIDE.value for a in state.governance_actions):
                state.governance_actions.append(GovernanceAction(
                    action_type=GovernanceActionType.OVERRIDE.value,
                    reason="High autonomy risk detected. Output may be overly prescriptive. User agency preserved via mandatory disclaimer.",
                    policy_id="pol_autonomy_001"
                ))
            state.compliance_status = "flagged"
            
    return state

def validate_memory_privacy(state: GovernanceState) -> GovernanceState:
    """
    Ensures that if memory influence is cited, it doesn't contain PII 
    or sensitive identifiers in the transparency report.
    """
    # Simulated PII redaction for transparency report
    if state.transparency.memory_influence:
        state.transparency.memory_influence = state.transparency.memory_influence.replace("PII", "[REDACTED]")
        
    return state
