from enum import Enum

class AgentRole(str, Enum):
    RESEARCH_AGENT = "research_agent"
    TECHNICAL_ANALYSIS_AGENT = "technical_analysis_agent"
    PHILOSOPHICAL_REFLECTION_AGENT = "philosophical_reflection_agent"
    STRATEGIC_REASONING_AGENT = "strategic_reasoning_agent"
    SEMANTIC_MAPPING_AGENT = "semantic_mapping_agent"
    CONTRADICTION_DETECTION_AGENT = "contradiction_detection_agent"
    SYNTHESIS_AGENT = "synthesis_agent"
    EXPLORATORY_CURIOSITY_AGENT = "exploratory_curiosity_agent"
    CRITICAL_THINKING_AGENT = "critical_thinking_agent"
    SYSTEMS_THINKING_AGENT = "systems_thinking_agent"

class CollaborationStrategy(str, Enum):
    PARALLEL_ANALYSIS = "parallel_analysis"
    SEQUENTIAL_REASONING = "sequential_reasoning"
    DEBATE_AND_CRITIQUE = "debate_and_critique"
    REFLECTIVE_SYNTHESIS = "reflective_synthesis"
    HIERARCHICAL_DELEGATION = "hierarchical_delegation"
    CONTRADICTION_RESOLUTION = "contradiction_resolution"
    EXPLORATION_EXPANSION = "exploration_expansion"
    MULTI_PERSPECTIVE_ANALYSIS = "multi_perspective_analysis"
    CONSENSUS_BUILDING = "consensus_building"
    ADVERSARIAL_REASONING = "adversarial_reasoning"
