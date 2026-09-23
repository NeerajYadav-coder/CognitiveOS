from src.schemas.cognitive import EvolutionState, EvolutionPlan
from src.services.evolution.taxonomy import OptimizationType

def enforce_governance_ceiling(state: EvolutionState) -> EvolutionState:
    """
    Ensures that no evolution recommendation targets the 'GovernanceEngine' 
    for optimization in a way that might reduce safety constraints.
    """
    pruned = []
    for rec in state.recommendations:
        if rec.target_engine == "GovernanceEngine":
            # Redact if it feels like it's weakening safety
            if "reduce" in rec.rationale.lower() or "skip" in rec.rationale.lower():
                continue
        pruned.append(rec)
    state.recommendations = pruned
    return state

def mandatory_human_approval(state: EvolutionState) -> EvolutionState:
    """
    Forcefully sets 'requires_human_approval' to True for all evolution plans,
    preventing any autonomous execution.
    """
    for plan in state.active_plans:
        plan.requires_human_approval = True
    return state

def validate_rollback_presence(state: EvolutionState) -> EvolutionState:
    """
    Ensures that every evolution plan has a defined rollback strategy.
    If missing, injects a standard 'Hard Reset' default.
    """
    for plan in state.active_plans:
        if not plan.rollback_strategy:
            plan.rollback_strategy = "Revert to last stable production schema and flush orchestration cache."
            
    return state
