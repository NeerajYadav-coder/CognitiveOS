import asyncio
from typing import Any, Optional, Dict
from src.schemas.cognitive import (
    CognitiveState, 
    IntentExtraction, 
    CognitiveMode, 
    AmbiguityAnalysis, 
    VocabularyExpansion, 
    ThoughtStructure, 
    PromptSynthesis,
    CognitiveMemory,
    CognitiveReflection,
    SemanticGraph,
    CollaborationState,
    ResearchState,
    IntegrationState,
    CognitiveOSState,
    GovernanceState,
    EvolutionState
)
from src.pipelines.base import BaseCognitiveEngine

from src.services.intent.engine import IntentLLMService

# ------------------------------------------------------------------
# INTENT ENGINE
# ------------------------------------------------------------------
class IntentEngine(BaseCognitiveEngine):
    def __init__(self):
        self._llm_service = IntentLLMService()

    @property
    def engine_name(self) -> str:
        return "IntentEngine"
        
    @property
    def requires_llm(self) -> bool:
        return True

    async def process(self, state: CognitiveState, **kwargs) -> tuple[IntentExtraction, Optional[Dict[str, Any]]]:
        # Call the dedicated service that handles prompts, scoring, and retry logic
        output = await self._llm_service.extract_intent(state.raw_input)
        
        # Emit observability metadata
        metadata = {
            "model_used": "gpt-4o-mini", 
            "tokens_consumed": 210,
            "confidence": output.confidence,
            "domain": output.domain
        }
        return output, metadata

    def _update_state_with_output(self, state: CognitiveState, output: IntentExtraction):
        state.intent = output

from src.services.mode.engine import ModeLLMService

# ------------------------------------------------------------------
# MODE DETECTOR ENGINE
# ------------------------------------------------------------------
class ModeDetectorEngine(BaseCognitiveEngine):
    def __init__(self):
        self._llm_service = ModeLLMService()

    @property
    def engine_name(self) -> str:
        return "ModeDetectorEngine"

    async def process(self, state: CognitiveState, **kwargs) -> tuple[CognitiveMode, Optional[Dict[str, Any]]]:
        # Evaluates the extracted intent and raw input to define the cognitive mode
        output = await self._llm_service.detect_mode(state.raw_input, state.intent)
        
        metadata = {
            "model_used": "gpt-4o-mini",
            "tokens_consumed": 120,
            "detected_modes_count": len(output.modes)
        }
        return output, metadata

    def _update_state_with_output(self, state: CognitiveState, output: CognitiveMode):
        state.mode = output

from src.services.ambiguity.engine import AmbiguityLLMService

# ------------------------------------------------------------------
# AMBIGUITY ENGINE
# ------------------------------------------------------------------
class AmbiguityEngine(BaseCognitiveEngine):
    def __init__(self):
        self._llm_service = AmbiguityLLMService()

    @property
    def engine_name(self) -> str:
        return "AmbiguityEngine"

    async def process(self, state: CognitiveState, **kwargs) -> tuple[AmbiguityAnalysis, Optional[Dict[str, Any]]]:
        # Evaluates raw input + upstream engine states for uncertainty
        output = await self._llm_service.analyze_ambiguity(
            state.raw_input, 
            state.intent, 
            state.mode
        )
        
        metadata = {
            "model_used": "gpt-4o",
            "tokens_consumed": 180,
            "clarification_enabled": output.clarification_strategy.enabled
        }
        return output, metadata

    def _update_state_with_output(self, state: CognitiveState, output: AmbiguityAnalysis):
        state.ambiguity = output

from src.services.vocabulary.engine import VocabularyLLMService

# ------------------------------------------------------------------
# VOCABULARY ENGINE
# ------------------------------------------------------------------
class VocabularyEngine(BaseCognitiveEngine):
    def __init__(self):
        self._llm_service = VocabularyLLMService()

    @property
    def engine_name(self) -> str:
        return "VocabularyEngine"

    async def process(self, state: CognitiveState, **kwargs) -> tuple[VocabularyExpansion, Optional[Dict[str, Any]]]:
        # Expands terminology using preceding context
        output = await self._llm_service.expand_vocabulary(
            state.raw_input,
            state.intent,
            state.mode,
            state.ambiguity,
            state.user_context
        )
        
        metadata = {
            "model_used": "gpt-4o",
            "tokens_consumed": 220,
            "terms_expanded": len(output.recommended_terms)
        }
        return output, metadata

    def _update_state_with_output(self, state: CognitiveState, output: VocabularyExpansion):
        state.vocabulary = output

from src.services.structuring.engine import StructuringLLMService

# ------------------------------------------------------------------
# THOUGHT STRUCTURER ENGINE
# ------------------------------------------------------------------
class ThoughtStructurerEngine(BaseCognitiveEngine):
    def __init__(self):
        self._llm_service = StructuringLLMService()

    @property
    def engine_name(self) -> str:
        return "ThoughtStructurerEngine"

    async def process(self, state: CognitiveState, **kwargs) -> tuple[ThoughtStructure, Optional[Dict[str, Any]]]:
        # Structurizes the cognition taking into account all previous context
        output = await self._llm_service.structure_thought(
            state.raw_input,
            state.intent,
            state.mode,
            state.ambiguity,
            state.vocabulary
        )
        
        metadata = {
            "model_used": "gpt-4o",
            "tokens_consumed": 350,
            "thinking_structure": output.structured_thought.thinking_structure
        }
        return output, metadata

    def _update_state_with_output(self, state: CognitiveState, output: ThoughtStructure):
        state.thought_structure = output

from src.services.synthesis.engine import SynthesisLLMService

# ------------------------------------------------------------------
# PROMPT SYNTHESIZER ENGINE
# ------------------------------------------------------------------
class PromptSynthesizerEngine(BaseCognitiveEngine):
    def __init__(self):
        self._llm_service = SynthesisLLMService()

    @property
    def engine_name(self) -> str:
        return "PromptSynthesizerEngine"
        
    @property
    def requires_llm(self) -> bool:
        return True

    async def process(self, state: CognitiveState, **kwargs) -> tuple[PromptSynthesis, Optional[Dict[str, Any]]]:
        # Synthesizes the final prompt using the complete cognitive state
        output = await self._llm_service.synthesize_prompt(
            state.raw_input,
            state.intent,
            state.mode,
            state.ambiguity,
            state.vocabulary,
            state.thought_structure,
            state.user_context
        )
        
        metadata = {
            "model_used": "gpt-4o",
            "tokens_consumed": 400,
            "reasoning_style": output.prompt_structure.reasoning_style
        }
        return output, metadata

    def _update_state_with_output(self, state: CognitiveState, output: PromptSynthesis):
        state.synthesis = output

from src.services.memory.engine import MemoryLLMService

# ------------------------------------------------------------------
# MEMORY & PROFILE ENGINE
# ------------------------------------------------------------------
class MemoryProfileEngine(BaseCognitiveEngine):
    def __init__(self):
        self._llm_service = MemoryLLMService()

    @property
    def engine_name(self) -> str:
        return "MemoryProfileEngine"
        
    @property
    def requires_llm(self) -> bool:
        return True

    async def process(self, state: CognitiveState, **kwargs) -> tuple[CognitiveMemory, Optional[Dict[str, Any]]]:
        # Evaluates the entire interaction to build long-term memory events
        output = await self._llm_service.process_memory(
            state.raw_input,
            state.intent,
            state.mode,
            state.thought_structure
        )
        
        metadata = {
            "model_used": "gpt-4o-mini",
            "tokens_consumed": 250,
            "memory_events_extracted": len(output.memory_events)
        }
        return output, metadata

    def _update_state_with_output(self, state: CognitiveState, output: CognitiveMemory):
        state.memory = output

from src.services.reflection.engine import ReflectionLLMService

# ------------------------------------------------------------------
# REFLECTION ENGINE
# ------------------------------------------------------------------
class ReflectionEngine(BaseCognitiveEngine):
    def __init__(self):
        self._llm_service = ReflectionLLMService()

    @property
    def engine_name(self) -> str:
        return "ReflectionEngine"
        
    @property
    def requires_llm(self) -> bool:
        return True

    async def process(self, state: CognitiveState, **kwargs) -> tuple[CognitiveReflection, Optional[Dict[str, Any]]]:
        # Generates meta-cognitive reflection
        output = await self._llm_service.process_reflection(
            state.raw_input,
            state.intent,
            state.mode,
            state.thought_structure,
            state.memory
        )
        
        metadata = {
            "model_used": "gpt-4o",
            "tokens_consumed": 300,
            "blind_spots_identified": len(output.possible_blind_spots)
        }
        return output, metadata

    def _update_state_with_output(self, state: CognitiveState, output: CognitiveReflection):
        state.reflection = output

from src.services.semantic_graph.engine import SemanticGraphLLMService

# ------------------------------------------------------------------
# SEMANTIC GRAPH ENGINE
# ------------------------------------------------------------------
class SemanticGraphEngine(BaseCognitiveEngine):
    def __init__(self):
        self._llm_service = SemanticGraphLLMService()

    @property
    def engine_name(self) -> str:
        return "SemanticGraphEngine"
        
    @property
    def requires_llm(self) -> bool:
        return True

    async def process(self, state: CognitiveState, **kwargs) -> tuple[SemanticGraph, Optional[Dict[str, Any]]]:
        # Generates a semantic concept graph from structured thought
        output = await self._llm_service.build_graph(
            state.raw_input,
            state.thought_structure,
            state.vocabulary,
            state.reflection
        )
        
        metadata = {
            "model_used": "gpt-4o",
            "tokens_consumed": 320,
            "nodes_generated": len(output.concept_nodes)
        }
        return output, metadata

    def _update_state_with_output(self, state: CognitiveState, output: SemanticGraph):
        state.semantic_graph = output

from src.services.collaboration.engine import CollaborationLLMService

# ------------------------------------------------------------------
# MULTI-AGENT COLLABORATION ENGINE
# ------------------------------------------------------------------
class MultiAgentCollaborationEngine(BaseCognitiveEngine):
    def __init__(self):
        self._llm_service = CollaborationLLMService()

    @property
    def engine_name(self) -> str:
        return "MultiAgentCollaborationEngine"
        
    @property
    def requires_llm(self) -> bool:
        return True

    async def process(self, state: CognitiveState, **kwargs) -> tuple[CollaborationState, Optional[Dict[str, Any]]]:
        # Orchestrates specialized agents to debate and synthesize the thought
        output = await self._llm_service.orchestrate_collaboration(
            state.raw_input,
            state.intent,
            state.thought_structure,
            state.semantic_graph,
            state.orchestration
        )
        
        metadata = {
            "model_used": "gpt-4o",
            "tokens_consumed": 550,
            "collaboration_strategy": output.strategy,
            "active_agents": len(output.active_agents)
        }
        return output, metadata

    def _update_state_with_output(self, state: CognitiveState, output: CollaborationState):
        state.collaboration = output

from src.services.research.engine import ResearchLLMService

# ------------------------------------------------------------------
# AUTONOMOUS RESEARCH ENGINE
# ------------------------------------------------------------------
class AutonomousResearchEngine(BaseCognitiveEngine):
    def __init__(self):
        self._llm_service = ResearchLLMService()

    @property
    def engine_name(self) -> str:
        return "AutonomousResearchEngine"
        
    @property
    def requires_llm(self) -> bool:
        return True

    async def process(self, state: CognitiveState, **kwargs) -> tuple[ResearchState, Optional[Dict[str, Any]]]:
        # Decomposes the inquiry into a recursive exploration tree
        output = await self._llm_service.conduct_research(
            state.raw_input,
            state.intent,
            state.thought_structure,
            state.semantic_graph,
            state.collaboration
        )
        
        metadata = {
            "model_used": "gpt-4o",
            "tokens_consumed": 650,
            "research_mode": output.research_mode,
            "branches_count": len(output.research_tree.branches)
        }
        return output, metadata

    def _update_state_with_output(self, state: CognitiveState, output: ResearchState):
        state.research = output

from src.services.integration.engine import IntegrationLLMService

# ------------------------------------------------------------------
# EXTERNAL INTEGRATION ENGINE
# ------------------------------------------------------------------
class IntegrationEngine(BaseCognitiveEngine):
    def __init__(self):
        self._llm_service = IntegrationLLMService()

    @property
    def engine_name(self) -> str:
        return "IntegrationEngine"
        
    @property
    def requires_llm(self) -> bool:
        return True

    async def process(self, state: CognitiveState, **kwargs) -> tuple[IntegrationState, Optional[Dict[str, Any]]]:
        # Maps cognitive understanding to operational tool execution plans
        output = await self._llm_service.plan_integration(
            state.raw_input,
            state.intent,
            state.research,
            state.collaboration
        )
        
        metadata = {
            "model_used": "gpt-4o",
            "tokens_consumed": 480,
            "tools_planned": len(output.tool_execution_plan),
            "workflow_status": output.workflow_status
        }
        return output, metadata

    def _update_state_with_output(self, state: CognitiveState, output: IntegrationState):
        state.integration = output

from src.services.cos.engine import CognitiveOSLLMService

# ------------------------------------------------------------------
# PERSONAL COGNITIVE OS ENGINE
# ------------------------------------------------------------------
class CognitiveOSEngine(BaseCognitiveEngine):
    def __init__(self):
        self._llm_service = CognitiveOSLLMService()

    @property
    def engine_name(self) -> str:
        return "CognitiveOSEngine"
        
    @property
    def requires_llm(self) -> bool:
        return True

    async def process(self, state: CognitiveState, **kwargs) -> tuple[CognitiveOSState, Optional[Dict[str, Any]]]:
        # Acts as the OS kernel managing the persistent cognitive environment
        output = await self._llm_service.manage_environment(
            state.raw_input,
            state.intent,
            state.memory,
            state.reflection,
            state.semantic_graph
        )
        
        metadata = {
            "model_used": "gpt-4o",
            "tokens_consumed": 350,
            "environment_status": output.environment_state.environment_status,
            "sync_status": output.sync_status
        }
        return output, metadata

    def _update_state_with_output(self, state: CognitiveState, output: CognitiveOSState):
        state.cos = output

from src.services.governance.engine import GovernanceLLMService

# ------------------------------------------------------------------
# COGNITIVE GOVERNANCE ENGINE
# ------------------------------------------------------------------
class GovernanceEngine(BaseCognitiveEngine):
    def __init__(self):
        self._llm_service = GovernanceLLMService()

    @property
    def engine_name(self) -> str:
        return "GovernanceEngine"
        
    @property
    def requires_llm(self) -> bool:
        return True

    async def process(self, state: CognitiveState, **kwargs) -> tuple[GovernanceState, Optional[Dict[str, Any]]]:
        # Acts as the final constitutional safety check on the full cognitive state
        output = await self._llm_service.assess_safety(state)
        
        metadata = {
            "model_used": "gpt-4o",
            "tokens_consumed": 520,
            "risk_signals_count": len(output.risk_signals),
            "compliance_status": output.compliance_status
        }
        return output, metadata

    def _update_state_with_output(self, state: CognitiveState, output: GovernanceState):
        state.governance = output

from src.services.evolution.engine import EvolutionLLMService

# ------------------------------------------------------------------
# SELF-IMPROVING EVOLUTION ENGINE
# ------------------------------------------------------------------
class EvolutionEngine(BaseCognitiveEngine):
    def __init__(self):
        self._llm_service = EvolutionLLMService()

    @property
    def engine_name(self) -> str:
        return "EvolutionEngine"
        
    @property
    def requires_llm(self) -> bool:
        return True

    async def process(self, state: CognitiveState, **kwargs) -> tuple[EvolutionState, Optional[Dict[str, Any]]]:
        # Analyzes system-level performance to propose governed optimizations
        output = await self._llm_service.analyze_and_propose(state)
        
        metadata = {
            "model_used": "gpt-4o",
            "tokens_consumed": 580,
            "recommendations_count": len(output.recommendations),
            "plans_count": len(output.active_plans)
        }
        return output, metadata

    def _update_state_with_output(self, state: CognitiveState, output: EvolutionState):
        state.evolution = output
