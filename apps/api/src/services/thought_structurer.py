"""
Thought Structuring Engine — CognitiveOS
Selects the optimal thinking framework and structures user thought
into coherent sections that guide LLM interaction.
"""
from __future__ import annotations

import time
from typing import Optional

import structlog
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config.settings import get_settings
from src.schemas.cognitive import (
    CognitiveMode,
    CognitiveModeResult,
    IntentExtractionResult,
    ThoughtFramework,
    ThoughtStructure,
    ThoughtSection,
)

logger = structlog.get_logger(__name__)
settings = get_settings()

# Framework selection heuristics
FRAMEWORK_FOR_MODE: dict[CognitiveMode, ThoughtFramework] = {
    CognitiveMode.EXPLORATORY: ThoughtFramework.TREE_OF_THOUGHT,
    CognitiveMode.ANALYTICAL: ThoughtFramework.CHAIN_OF_THOUGHT,
    CognitiveMode.CREATIVE: ThoughtFramework.COMPARE_CONTRAST,
    CognitiveMode.CRITICAL: ThoughtFramework.SOCRATIC,
    CognitiveMode.SYNTHETIC: ThoughtFramework.FIRST_PRINCIPLES,
    CognitiveMode.PROCEDURAL: ThoughtFramework.PROBLEM_SOLUTION,
    CognitiveMode.REFLECTIVE: ThoughtFramework.FIVE_WS,
    CognitiveMode.UNKNOWN: ThoughtFramework.CHAIN_OF_THOUGHT,
}

STRUCTURING_SYSTEM_PROMPT = """
You are the Thought Structuring Engine for CognitiveOS.
Your role is to organize a user's cognitive intent into a structured framework
that will enable an LLM to respond with maximum utility and depth.

Frameworks available:
- chain-of-thought: Sequential logical reasoning steps
- problem-solution: State problem clearly, then solution structure
- compare-contrast: Examine multiple perspectives or options
- cause-effect: Identify causes, effects, and relationships
- five-ws: Who, What, Where, When, Why + How
- socratic: Question-driven examination of assumptions
- first-principles: Break down to fundamental truths
- tree-of-thought: Branching exploration of possibilities
- custom: Custom structure for unique cases

Select the MOST APPROPRIATE framework for the cognitive mode and intent.
Return the thought organized into clear, weighted sections.

Return ONLY valid JSON.
"""

STRUCTURING_USER_TEMPLATE = """
Structure this cognitive intent:

Core Intent: {core_intent}
Sub-Intents: {sub_intents}
Cognitive Mode: {cognitive_mode}
Recommended Framework: {recommended_framework}
Domain Context: {domain_hints}
Vocabulary Highlights: {vocab_highlights}

Return JSON with:
- framework: selected framework name
- sections: list of {{title, content, weight}} — organize the thought into 3-5 sections
- logical_flow: list of strings describing the thinking progression
- key_constraints: list of important constraints or boundaries
- output_format: preferred output format (markdown/bullet-list/structured/conversational)
"""


class ThoughtStructurer:
    """
    Thought Structuring Engine.
    Selects thinking frameworks and organizes intent into coherent structure.
    """

    def __init__(self, client: Optional[AsyncOpenAI] = None) -> None:
        self._client = client or AsyncOpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_API_BASE)
        self._model = settings.OPENAI_MODEL
        self._log = logger.bind(engine="thought-structurer")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
    )
    async def structure(
        self,
        intent_result: IntentExtractionResult,
        mode_result: CognitiveModeResult,
        vocab_highlights: list[str] | None = None,
        session_id: Optional[str] = None,
    ) -> ThoughtStructure:
        """
        Structure user thought using the appropriate cognitive framework.

        Args:
            intent_result: Output from Intent Engine
            mode_result: Output from Mode Detector
            vocab_highlights: Key terms from Vocabulary Engine
            session_id: Optional session context

        Returns:
            ThoughtStructure with framework and organized sections
        """
        start = time.perf_counter()
        log = self._log.bind(session_id=session_id)

        recommended_framework = FRAMEWORK_FOR_MODE.get(
            mode_result.primary, ThoughtFramework.CHAIN_OF_THOUGHT
        )
        log.info("Structuring thought", recommended_framework=recommended_framework.value)

        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": STRUCTURING_SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": STRUCTURING_USER_TEMPLATE.format(
                            core_intent=intent_result.core_intent,
                            sub_intents=", ".join(intent_result.sub_intents) or "none",
                            cognitive_mode=mode_result.primary.value,
                            recommended_framework=recommended_framework.value,
                            domain_hints=", ".join(intent_result.domain_hints) or "general",
                            vocab_highlights=", ".join(vocab_highlights or []) or "none",
                        ),
                    },
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=2000,
            )

            raw_json = response.choices[0].message.content
            result = ThoughtStructure.model_validate_json(raw_json)

            elapsed = (time.perf_counter() - start) * 1000
            log.info(
                "Thought structure complete",
                framework=result.framework,
                sections=len(result.sections),
                elapsed_ms=round(elapsed, 2),
            )
            return result

        except Exception as e:
            elapsed = (time.perf_counter() - start) * 1000
            log.error("Thought structuring failed", error=str(e), elapsed_ms=round(elapsed, 2))
            return self._minimal_fallback(intent_result, recommended_framework)

    def _minimal_fallback(
        self,
        intent_result: IntentExtractionResult,
        framework: ThoughtFramework,
    ) -> ThoughtStructure:
        return ThoughtStructure(
            framework=framework,
            sections=[
                ThoughtSection(
                    title="Core Intent",
                    content=intent_result.core_intent,
                    weight=1.0,
                ),
                ThoughtSection(
                    title="Context",
                    content=intent_result.raw_input,
                    weight=0.8,
                ),
            ],
            logical_flow=["State intent", "Provide context", "Request response"],
            key_constraints=[],
            output_format="markdown",
        )
