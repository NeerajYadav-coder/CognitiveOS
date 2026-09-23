from enum import Enum

class GovernanceDomain(str, Enum):
    MANIPULATION_PREVENTION = "manipulation_prevention"
    AUTONOMY_PRESERVATION = "autonomy_preservation"
    TRANSPARENCY_ENFORCEMENT = "transparency_enforcement"
    PRIVACY_PROTECTION = "privacy_protection"
    DEPENDENCY_PREVENTION = "dependency_prevention"
    MEMORY_GOVERNANCE = "memory_governance"
    ETHICAL_PERSONALIZATION = "ethical_personalization"
    AGENT_SAFETY = "agent_safety"
    RESEARCH_BOUNDARIES = "research_boundaries"
    HUMAN_OVERSIGHT = "human_oversight"

class GovernanceActionType(str, Enum):
    ALLOW = "allow"
    FLAG = "flag"
    REDACT = "redact"
    OVERRIDE = "override"
