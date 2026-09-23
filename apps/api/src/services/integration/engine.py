import asyncio
from typing import Optional

from src.schemas.cognitive import (
    IntegrationState,
    ToolCall,
    IntegrationResult,
    IntentExtraction,
    ResearchState,
    CollaborationState
)
from src.services.integration.taxonomy import IntegrationCategory, ToolPermissionLevel
from src.services.integration.heuristics import (
    validate_permission_boundaries,
    sanitize_tool_parameters,
    enforce_rate_limits
)
from src.utils.logger import logger

class IntegrationLLMService:
    """
    Abstracts LLM communication for the External Tooling & Integration Engine.
    Maps cognitive context to operational execution plans.
    """
    
    async def plan_integration(
        self,
        raw_input: str,
        intent: Optional[IntentExtraction],
        research: Optional[ResearchState],
        collaboration: Optional[CollaborationState]
    ) -> IntegrationState:
        
        logger.debug("Calling LLM for Integration Planning...")
        
        # Simulate LLM Network Call
        await asyncio.sleep(0.4)
        
        raw_lower = raw_input.lower()
        
        # ── Research-Driven Integration ──────────────────────────
        if research and len(research.knowledge_gaps) > 0:
            calls = [
                ToolCall(
                    tool_id="google_search_v1",
                    tool_name="Google Search",
                    parameters={"query": research.knowledge_gaps[0].concept},
                    permission_level_required=ToolPermissionLevel.LOW.value
                ),
                ToolCall(
                    tool_id="arxiv_api_v2",
                    tool_name="ArXiv Research Explorer",
                    parameters={"subject": research.knowledge_gaps[0].concept},
                    permission_level_required=ToolPermissionLevel.LOW.value
                )
            ]
            status = "executing"
            
        # ── Operational / Actionable ─────────────────────────────
        elif "schedule" in raw_lower or "calendar" in raw_lower:
            calls = [
                ToolCall(
                    tool_id="gcal_insert_v1",
                    tool_name="Google Calendar",
                    parameters={"summary": "Cognitive Focus Session", "duration": 60},
                    permission_level_required=ToolPermissionLevel.HIGH.value
                )
            ]
            status = "awaiting_approval"
            
        # ── Default / Analytics ──────────────────────────────────
        else:
            calls = [
                ToolCall(
                    tool_id="analytics_collector",
                    tool_name="Cognitive Analytics",
                    parameters={"metric": "intent_depth", "value": intent.depth_level if intent else "unknown"},
                    permission_level_required=ToolPermissionLevel.LOW.value
                )
            ]
            status = "completed"

        state = IntegrationState(
            tool_execution_plan=calls,
            integration_results=[],
            workflow_status=status,
            external_context_captured={},
            confidence=0.89
        )
        
        # Apply Safety & Security Heuristics
        state = sanitize_tool_parameters(state)
        state = enforce_rate_limits(state)
        state = validate_permission_boundaries(state)
        
        return state
