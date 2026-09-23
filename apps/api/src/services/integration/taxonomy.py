from enum import Enum

class IntegrationCategory(str, Enum):
    SEARCH_ENGINES = "search_engines"
    ACADEMIC_RESEARCH = "academic_research"
    PRODUCTIVITY = "productivity"
    KNOWLEDGE_MANAGEMENT = "knowledge_management"
    FILE_SYSTEM = "file_system"
    CALENDAR = "calendar"
    COMMUNICATION = "communication"
    DEVOPS = "devops"
    ANALYTICS = "analytics"
    AGENT_TOOLING = "agent_tooling"

class ToolPermissionLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
