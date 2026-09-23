from enum import Enum

class OSModule(str, Enum):
    KNOWLEDGE_SPACE = "knowledge_space"
    STRATEGIC_WORKSPACE = "strategic_workspace"
    RESEARCH_ENVIRONMENT = "research_environment"
    CURIOSITY_SYSTEM = "curiosity_system"
    REFLECTION_DASHBOARD = "reflection_dashboard"
    SEMANTIC_INTERFACE = "semantic_interface"
    INQUIRY_MAPPING = "inquiry_mapping"
    MULTI_AGENT_WORKSPACE = "multi_agent_workspace"
    INTELLECTUAL_TIMELINE = "intellectual_timeline"
    ADAPTIVE_ASSISTANCE = "adaptive_assistance"

class EnvironmentStatus(str, Enum):
    FOCUSED = "focused"
    EXPLORATORY = "exploratory"
    REFLECTIVE = "reflective"
    IDLE = "idle"
