from enum import Enum

class EvolutionDomain(str, Enum):
    ORCHESTRATION_EFFICIENCY = "orchestration_efficiency"
    RETRIEVAL_OPTIMIZATION = "retrieval_optimization"
    RESEARCH_WORKFLOW = "research_workflow"
    AGENT_COORDINATION = "agent_coordination"
    PROMPT_SYNTHESIS = "prompt_synthesis"
    REFLECTION_QUALITY = "reflection_quality"
    ROUTING_OPTIMIZATION = "routing_optimization"
    WORKSPACE_EVOLUTION = "workspace_evolution"
    PERSONALIZATION_CALIBRATION = "personalization_calibration"
    SAFETY_ADAPTATION = "safety_adaptation"

class OptimizationType(str, Enum):
    PROMPT_REFINEMENT = "prompt_refinement"
    HEURISTIC_TUNING = "heuristic_tuning"
    ORCHESTRATION_ROUTING = "orchestration_routing"
    SCHEMA_EVOLUTION = "schema_evolution"
    WORKFLOW_PRUNING = "workflow_pruning"
