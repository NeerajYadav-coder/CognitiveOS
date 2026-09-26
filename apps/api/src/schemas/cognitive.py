from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone

class IntentExtraction(BaseModel):
    primary_intent: str = Field(description="The main goal of the user")
    secondary_intents: List[str] = Field(default_factory=list, description="Sub-goals or implicit goals")
    domain: str = Field(description="The core knowledge domain (e.g., Software Architecture, General Trivia)")
    depth_level: str = Field(description="The required cognitive depth (e.g., beginner, expert, exploratory)")
    confidence: float = Field(ge=0.0, le=1.0)

class ModeScore(BaseModel):
    name: str = Field(description="Name of the cognitive mode")
    score: float = Field(ge=0.0, le=1.0, description="Probability score of this mode")

class CognitiveMode(BaseModel):
    modes: List[ModeScore] = Field(description="List of detected cognitive modes with scores")
    primary_mode: str = Field(description="The highest scoring or most dominant mode")
    confidence: float = Field(ge=0.0, le=1.0, description="Overall confidence in this classification profile")

class ClarificationStrategy(BaseModel):
    enabled: bool = Field(description="Whether clarification questions should be asked")
    question_count: int = Field(ge=0, le=5, description="Number of questions to ask")
    depth: str = Field(description="Depth level: 'light', 'medium', 'deep'")
    preserve_exploration: bool = Field(description="If true, do not force precision, maintain open-endedness")

class AmbiguityAnalysis(BaseModel):
    ambiguity_score: float = Field(ge=0.0, le=1.0, description="Overall ambiguity level")
    ambiguity_type: List[str] = Field(description="List of detected ambiguity taxonomy labels")
    clarification_strategy: ClarificationStrategy = Field(description="Recommended action plan for clarification")
    confidence: float = Field(ge=0.0, le=1.0, description="Engine's confidence in this analysis")

class SemanticExpansion(BaseModel):
    term: str = Field(description="The precise technical or philosophical terminology")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence that this term matches the user's implicit intent")
    domain: str = Field(description="The knowledge domain this term belongs to")

class VocabularyExpansion(BaseModel):
    core_expression: str = Field(description="The raw thought distilled into a core phrase")
    semantic_expansions: List[SemanticExpansion] = Field(default_factory=list, description="Precise terminology mappings")
    adjacent_concepts: List[str] = Field(default_factory=list, description="Broader or tangential concepts worth exploring")
    recommended_terms: List[str] = Field(default_factory=list, description="List of the best terms to inject into the final prompt")

class StructuredThought(BaseModel):
    core_question: str = Field(description="The fundamental inquiry distilled from the chaos")
    exploration_direction: str = Field(description="The suggested angle or lens to approach the thought")
    subtopics: List[str] = Field(default_factory=list, description="Decomposed elements of the thought")
    missing_context: List[str] = Field(default_factory=list, description="Context gaps identified during structuring")
    possible_domains: List[str] = Field(default_factory=list, description="Domains this thought touches upon")
    thinking_structure: str = Field(description="The primary cognitive framework applied (e.g., exploratory, analytical)")

class ThoughtStructure(BaseModel):
    structured_thought: StructuredThought = Field(description="The decomposed and organized cognitive representation")
    clarified_representation: str = Field(description="A clean, structured narrative of the original raw thought")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in the structural fidelity")

class PromptStructure(BaseModel):
    context: str = Field(description="Background and contextual framing for the LLM")
    objective: str = Field(description="The core task or goal for the LLM")
    constraints: List[str] = Field(default_factory=list, description="Rules the LLM must follow")
    depth_level: str = Field(description="Required depth of reasoning")
    reasoning_style: str = Field(description="How the LLM should think (e.g., Socratic, Step-by-step)")

class PromptSynthesis(BaseModel):
    final_prompt: str = Field(description="The fully structured and optimized prompt string to be sent to the LLM")
    prompt_structure: PromptStructure = Field(description="The decomposed structure of the prompt")
    optimization_notes: List[str] = Field(default_factory=list, description="Notes on what was optimized from the raw input")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in prompt quality")

class CognitiveMetadata(BaseModel):
    model_config = {"extra": "allow", "protected_namespaces": ()}
    processing_time_ms: float = 0.0
    model_used: Optional[str] = None
    tokens_consumed: int = 0
    engine_version: str = "1.0"
    confidence: float = 0.0

class CognitiveProfileUpdates(BaseModel):
    dominant_modes: List[str] = Field(default_factory=list, description="Recurring cognitive modes")
    recurring_domains: List[str] = Field(default_factory=list, description="Frequent domains of interest")
    exploration_patterns: List[str] = Field(default_factory=list, description="How the user explores ideas")
    depth_preference: str = Field(description="Typical desired depth of interaction")
    reasoning_style: str = Field(description="Preferred reasoning approach")

class MemoryEvent(BaseModel):
    category: str = Field(description="Memory category from taxonomy")
    content: str = Field(description="The actual memory or trend observed")
    temporal_weight: float = Field(ge=0.0, le=1.0, description="How relevant this is for long-term memory")

class CognitiveMemory(BaseModel):
    cognitive_profile_updates: CognitiveProfileUpdates
    memory_events: List[MemoryEvent] = Field(default_factory=list)
    adaptation_signals: List[str] = Field(default_factory=list, description="Directives on how to adapt future interactions")
    confidence: float = Field(ge=0.0, le=1.0)

class ReflectionSummary(BaseModel):
    dominant_themes: List[str] = Field(default_factory=list, description="Major intellectual themes identified")
    emerging_interests: List[str] = Field(default_factory=list, description="New domains or ideas the user is exploring")
    cognitive_shifts: List[str] = Field(default_factory=list, description="Observed changes in how the user approaches problems")
    reasoning_patterns: List[str] = Field(default_factory=list, description="Recurring logic or thinking structures")
    exploration_trends: List[str] = Field(default_factory=list, description="How curiosity is evolving")

class CognitiveReflection(BaseModel):
    reflection_summary: ReflectionSummary
    possible_blind_spots: List[str] = Field(default_factory=list, description="Areas the user might be overlooking")
    growth_signals: List[str] = Field(default_factory=list, description="Indicators of intellectual development")
    confidence: float = Field(ge=0.0, le=1.0)

class SemanticNode(BaseModel):
    id: str = Field(description="Unique identifier for the concept")
    label: str = Field(description="The human-readable concept name")
    domain: str = Field(description="Primary domain of the concept")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Contextual properties")

class SemanticRelationship(BaseModel):
    source: str = Field(description="Source node id")
    target: str = Field(description="Target node id")
    relationship_type: str = Field(description="Taxonomy classification of the link")
    confidence: float = Field(ge=0.0, le=1.0, description="Probabilistic strength of the connection")
    explanation: str = Field(description="Why these concepts are connected")

class ExplorationPath(BaseModel):
    path_name: str
    nodes: List[str] = Field(description="Ordered list of node IDs to traverse")
    rationale: str = Field(description="Why this path is intellectually valuable")

class SemanticGraph(BaseModel):
    concept_nodes: List[SemanticNode] = Field(default_factory=list)
    semantic_relationships: List[SemanticRelationship] = Field(default_factory=list)
    adjacent_domains: List[str] = Field(default_factory=list)
    exploration_paths: List[ExplorationPath] = Field(default_factory=list)
    semantic_clusters: List[Dict[str, List[str]]] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)

class OrchestrationDecision(BaseModel):
    engine_name: str
    action: str = Field(description="'execute', 'skip', 'defer'")
    reason: str = Field(description="Why this decision was made")

class ExecutionPlan(BaseModel):
    pipeline: List[str] = Field(description="The planned sequence of engines")
    routing_decisions: List[OrchestrationDecision] = Field(default_factory=list)
    adaptive_modifications: List[str] = Field(default_factory=list, description="How the plan deviated from default")

class OrchestrationState(BaseModel):
    execution_plan: ExecutionPlan
    current_engine_index: int = 0
    confidence: float = Field(ge=0.0, le=1.0)

class AgentMessage(BaseModel):
    agent_role: str = Field(description="Role from the taxonomy")
    content: str = Field(description="The cognitive output or critique")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Reasoning context")

class CollaborationState(BaseModel):
    strategy: str = Field(description="The chosen collaboration mode (e.g. Debate, Parallel Analysis)")
    active_agents: List[str] = Field(description="Agents involved in this task")
    agent_outputs: List[AgentMessage] = Field(default_factory=list, description="Outputs from individual agents")
    synthesized_insight: Optional[str] = Field(default=None, description="The final merged cognitive insight")
    confidence: float = Field(ge=0.0, le=1.0)

class ResearchNode(BaseModel):
    id: str
    inquiry: str = Field(description="The specific sub-question or exploration branch")
    depth_level: int = Field(description="How deep in the recursive tree this node is")
    status: str = Field(description="'pending', 'explored', 'abandoned'")

class ExplorationTree(BaseModel):
    root_inquiry: str
    branches: List[ResearchNode] = Field(default_factory=list)

class KnowledgeGap(BaseModel):
    concept: str = Field(description="The area where knowledge is missing or contradictory")
    impact: str = Field(description="How this gap affects the overall understanding")

class ResearchState(BaseModel):
    research_mode: str = Field(description="The chosen research strategy")
    research_tree: ExplorationTree
    knowledge_gaps: List[KnowledgeGap] = Field(default_factory=list)
    synthesized_understanding: Optional[str] = Field(default=None)
    confidence: float = Field(ge=0.0, le=1.0)

class ToolCall(BaseModel):
    tool_id: str
    tool_name: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    permission_level_required: str = Field(description="'low', 'medium', 'high', 'critical'")

class IntegrationResult(BaseModel):
    tool_id: str
    status: str = Field(description="'success', 'failed', 'pending_approval'")
    output: Optional[Any] = None
    execution_time_ms: float = 0.0

class IntegrationState(BaseModel):
    tool_execution_plan: List[ToolCall] = Field(default_factory=list)
    integration_results: List[IntegrationResult] = Field(default_factory=list)
    workflow_status: str = Field(description="'idle', 'executing', 'awaiting_approval', 'completed'")
    external_context_captured: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(ge=0.0, le=1.0)

class StrategicFocus(BaseModel):
    area: str
    priority: float = Field(ge=0.0, le=1.0)
    current_objective: str

class WorkspaceState(BaseModel):
    active_exploration_domains: List[str] = Field(default_factory=list)
    strategic_focus_areas: List[StrategicFocus] = Field(default_factory=list)
    environment_status: str = Field(description="'focused', 'exploratory', 'reflective', 'idle'")

class CognitiveOSState(BaseModel):
    environment_state: WorkspaceState
    adaptive_assistance_note: Optional[str] = Field(default=None)
    timeline_event_id: Optional[str] = None
    sync_status: str = Field(default="synchronized")
    confidence: float = Field(ge=0.0, le=1.0)

class RiskSignal(BaseModel):
    domain: str = Field(description="e.g. 'manipulation', 'autonomy', 'privacy'")
    score: float = Field(ge=0.0, le=1.0)
    description: str

class GovernanceAction(BaseModel):
    action_type: str = Field(description="'allow', 'flag', 'redact', 'override'")
    reason: str
    policy_id: str

class TransparencyReport(BaseModel):
    decisions_summary: str
    activated_engines: List[str]
    memory_influence: Optional[str] = None
    agent_contributions: List[str] = Field(default_factory=list)

class GovernanceState(BaseModel):
    safety_assessment: str
    risk_signals: List[RiskSignal] = Field(default_factory=list)
    governance_actions: List[GovernanceAction] = Field(default_factory=list)
    transparency: TransparencyReport
    compliance_status: str = Field(default="compliant")
    confidence: float = Field(ge=0.0, le=1.0)

class EvolutionRecommendation(BaseModel):
    target_engine: str
    optimization_type: str = Field(description="e.g. 'prompt_refinement', 'heuristic_tuning', 'orchestration_routing'")
    rationale: str
    impact_prediction: str

class EvolutionPlan(BaseModel):
    plan_id: str
    steps: List[str]
    requires_human_approval: bool = True
    rollback_strategy: str

class EvolutionState(BaseModel):
    recommendations: List[EvolutionRecommendation] = Field(default_factory=list)
    active_plans: List[EvolutionPlan] = Field(default_factory=list)
    performance_metrics_summary: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(ge=0.0, le=1.0)

class FeedbackRequest(BaseModel):
    session_id: str
    rating: int = Field(ge=1, le=5, description="User rating from 1 to 5")
    feedback_text: Optional[str] = Field(default=None, description="Optional text feedback")

class EngineResult(BaseModel):
    engine_name: str
    status: str = Field(description="'success', 'failed', 'skipped'")
    output: Optional[Any] = None
    metadata: CognitiveMetadata = Field(default_factory=CognitiveMetadata)
    error: Optional[str] = None

class DomainExpertise(BaseModel):
    domain: str
    level: str = Field("intermediate", description="novice, intermediate, advanced, expert")

class UserContext(BaseModel):
    user_id: str
    profession: Optional[str] = Field(None, description="e.g., Software Architect, Student, Layman")
    intellectual_level: str = Field("intermediate", description="novice, intermediate, advanced, expert")
    cognitive_style: Dict[str, str] = Field(
        default_factory=lambda: {
            "verbosity": "balanced",
            "reasoning_preference": "balanced",
        }
    )
    domain_expertise: List[DomainExpertise] = Field(default_factory=list)

class CognitiveState(BaseModel):
    """
    The central state object passed through the pipeline.
    It acts as the shared context for all engines.
    """
    session_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    raw_input: str
    user_context: Optional[UserContext] = None
    
    intent: Optional[IntentExtraction] = None
    mode: Optional[CognitiveMode] = None
    ambiguity: Optional[AmbiguityAnalysis] = None
    vocabulary: Optional[VocabularyExpansion] = None
    thought_structure: Optional[ThoughtStructure] = None
    synthesis: Optional[PromptSynthesis] = None
    memory: Optional[CognitiveMemory] = None
    reflection: Optional[CognitiveReflection] = None
    semantic_graph: Optional[SemanticGraph] = None
    orchestration: Optional[OrchestrationState] = None
    collaboration: Optional[CollaborationState] = None
    research: Optional[ResearchState] = None
    integration: Optional[IntegrationState] = None
    cos: Optional[CognitiveOSState] = None
    governance: Optional[GovernanceState] = None
    evolution: Optional[EvolutionState] = None
    
    metadata: CognitiveMetadata = Field(default_factory=CognitiveMetadata)
    engine_results: List[EngineResult] = Field(default_factory=list)
    global_metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def add_result(self, result: EngineResult):
        self.engine_results.append(result)

class SpokenThoughtAnalysis(BaseModel):
    cleaned_transcript: str = Field(description="Transcript with verbal fillers and disfluencies removed")
    filler_words_removed: List[str] = Field(default_factory=list, description="Verbal fillers filtered out")
    implicit_intent: str = Field(description="The underlying goal distilled from the spoken thought")
    latent_hypotheses: List[str] = Field(default_factory=list, description="Implicit assumptions or hypotheses discovered")
    spoken_ambiguity_score: float = Field(ge=0.0, le=1.0, description="Ambiguity rating of spoken thoughts")
    focal_question: str = Field(description="A single crisp clarifying question to sharpen the spoken thought")
    suggested_prompt: str = Field(description="Synthesized prompt ready for LLM dispatch")

class GraphNode(BaseModel):
    id: str
    label: str
    type: Optional[str] = None
    domain: Optional[str] = None

class GraphEdge(BaseModel):
    id: Optional[str] = None
    source: str
    target: str
    relation: Optional[str] = None

class GraphSynthesisRequest(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge] = []
    goal: Optional[str] = None

class GraphSynthesisResponse(BaseModel):
    title: str
    core_theme: str
    conceptual_pathways: List[str]
    synthesized_prompt: str
    recommended_framework: str

