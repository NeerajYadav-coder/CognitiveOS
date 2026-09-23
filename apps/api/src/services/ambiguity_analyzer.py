"""
Ambiguity Analyzer — CognitiveOS
Identifies vague, underspecified, or multi-interpretable aspects of user input
and generates targeted clarifying questions.
"""
from __future__ import annotations

import time
from typing import Optional

import structlog
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config.settings import get_settings
from src.schemas.cognitive import (
    AmbiguityAnalysis,
    AmbiguityLevel,
    AmbiguousTerm,
    IntentExtractionResult,
    CognitiveModeResult,
)

logger = structlog.get_logger(__name__)
settings = get_settings()

AMBIGUITY_SYSTEM_PROMPT = """
You are the Ambiguity Analysis Engine for CognitiveOS.
Your role is to identify unclear, vague, or multi-interpretable elements in 
user input, then generate precise clarifying questions that will resolve ambiguity.

Analyze for:
1. AMBIGUOUS TERMS — words with multiple valid interpretations in context
2. MISSING CONTEXT — information that is assumed but not stated
3. SCOPE AMBIGUITY — is the user asking broadly or narrowly?
4. INTENT AMBIGUITY — could this serve multiple fundamentally different purposes?
5. TEMPORAL AMBIGUITY — is the timeframe unclear?

Generate CLARIFYING QUESTIONS that are:
- Specific, not generic
- Ordered by importance
- Non-redundant
- Maximum 3 questions unless ambiguity is critical

Return ONLY valid JSON.
"""

AMBIGUITY_USER_TEMPLATE = """
Analyze ambiguity in this user input:

Raw Input: "{raw_input}"
Core Intent: {core_intent}
Cognitive Mode: {cognitive_mode}
Ambiguity Level (from intent engine): {ambiguity_level}

Return JSON with:
- level: refined ambiguity level (none/low/medium/high/critical)
- score: 0-100 numeric ambiguity score
- ambiguous_terms: list of {{term, possible_meanings, recommended_interpretation, confidence}}
- missing_context: list of missing contextual elements
- clarifying_questions: list of targeted questions (max 3 unless critical)
- can_proceed_without_clarification: boolean
"""


class AmbiguityAnalyzer:
    """
    Ambiguity Analysis Engine.
    Surfaces unclear elements and generates targeted clarifying questions.
    """

    def __init__(self, client: Optional[AsyncOpenAI] = None) -> None:
        self._client = client or AsyncOpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_API_BASE)
        self._model = settings.OPENAI_MODEL
        self._log = logger.bind(engine="ambiguity-analyzer")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
    )
    async def analyze(
        self,
        intent_result: IntentExtractionResult,
        mode_result: CognitiveModeResult,
        session_id: Optional[str] = None,
    ) -> AmbiguityAnalysis:
        """
        Analyze ambiguity in the user's input.

        Args:
            intent_result: Output from Intent Engine
            mode_result: Output from Mode Detector
            session_id: Optional session context

        Returns:
            AmbiguityAnalysis with terms, questions, and recommendation
        """
        start = time.perf_counter()
        log = self._log.bind(session_id=session_id)
        log.info("Analyzing ambiguity")

        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": AMBIGUITY_SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": AMBIGUITY_USER_TEMPLATE.format(
                            raw_input=intent_result.raw_input,
                            core_intent=intent_result.core_intent,
                            cognitive_mode=mode_result.primary.value,
                            ambiguity_level=intent_result.ambiguity_level.value,
                        ),
                    },
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
                max_tokens=1024,
            )

            raw_json = response.choices[0].message.content
            result = AmbiguityAnalysis.model_validate_json(raw_json)

            elapsed = (time.perf_counter() - start) * 1000
            log.info(
                "Ambiguity analysis complete",
                level=result.level,
                score=result.score,
                can_proceed=result.can_proceed_without_clarification,
                elapsed_ms=round(elapsed, 2),
            )
            return result

        except Exception as e:
            elapsed = (time.perf_counter() - start) * 1000
            log.error("Ambiguity analysis failed", error=str(e), elapsed_ms=round(elapsed, 2))
            return self._minimal_fallback(intent_result)

    def _minimal_fallback(
        self, intent_result: IntentExtractionResult
    ) -> AmbiguityAnalysis:
        """Returns a safe, minimal ambiguity result that allows pipeline continuation."""
        return AmbiguityAnalysis(
            level=intent_result.ambiguity_level,
            score=50.0,
            ambiguous_terms=[],
            missing_context=[],
            clarifying_questions=[],
            can_proceed_without_clarification=True,
        )
