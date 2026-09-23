"""
Intent Engine — CognitiveOS
Extracts core intent, sub-intents, signals and domain hints from raw user input.
Uses OpenAI structured outputs with Pydantic schemas for deterministic parsing.
"""
from __future__ import annotations

import time
from typing import Optional

import structlog
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config.settings import get_settings
from src.schemas.cognitive import (
    AmbiguityLevel,
    IntentExtractionResult,
    IntentSignal,
)

logger = structlog.get_logger(__name__)
settings = get_settings()

INTENT_EXTRACTION_SYSTEM_PROMPT = """
You are the Intent Extraction Engine of CognitiveOS — a cognitive infrastructure system.
Your role is to deeply analyze raw user input and extract its cognitive intent structure.

You must identify:
1. The CORE INTENT — the fundamental purpose or goal behind the input
2. SUB-INTENTS — supporting goals or secondary objectives
3. SIGNALS — observable cues in the language that reveal thinking type
4. DOMAIN HINTS — subject areas, fields, or contexts implied
5. AMBIGUITY LEVEL — how unclear or underspecified the input is

You are NOT a task executor. You are a cognitive analyst.
Respond ONLY in valid JSON matching the provided schema.
"""

INTENT_EXTRACTION_USER_TEMPLATE = """
Analyze the following raw user input and extract its intent structure:

<input>
{raw_input}
</input>

Return a JSON object with:
- raw_input: the original text
- core_intent: single sentence describing the fundamental goal
- sub_intents: list of secondary objectives (may be empty)
- signals: list of objects with 'type' and 'weight' (0.0-1.0)
  Signal types: question, command, exploration, clarification, task, emotional
- domain_hints: list of inferred subject domains
- confidence: overall confidence score (0.0-1.0)
- ambiguity_level: one of "none", "low", "medium", "high", "critical"
"""


class IntentEngine:
    """
    Intent Extraction Engine.
    Analyzes raw user input to surface core intent, sub-intents, 
    cognitive signals, and domain context.
    """

    def __init__(self, client: Optional[AsyncOpenAI] = None) -> None:
        self._client = client or AsyncOpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_API_BASE)
        self._model = settings.OPENAI_MODEL
        self._log = logger.bind(engine="intent-engine")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
    )
    async def extract(
        self,
        raw_input: str,
        session_id: Optional[str] = None,
    ) -> IntentExtractionResult:
        """
        Extract intent structure from raw user input.

        Args:
            raw_input: The user's raw text input
            session_id: Optional session context

        Returns:
            IntentExtractionResult with structured intent data
        """
        start = time.perf_counter()
        log = self._log.bind(session_id=session_id, input_length=len(raw_input))
        log.info("Starting intent extraction")

        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": INTENT_EXTRACTION_SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": INTENT_EXTRACTION_USER_TEMPLATE.format(
                            raw_input=raw_input
                        ),
                    },
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
                max_tokens=1024,
            )

            raw_json = response.choices[0].message.content
            result = IntentExtractionResult.model_validate_json(raw_json)

            elapsed = (time.perf_counter() - start) * 1000
            log.info(
                "Intent extraction complete",
                core_intent=result.core_intent,
                ambiguity=result.ambiguity_level,
                confidence=result.confidence,
                elapsed_ms=round(elapsed, 2),
            )

            return result

        except Exception as e:
            elapsed = (time.perf_counter() - start) * 1000
            log.error("Intent extraction failed", error=str(e), elapsed_ms=round(elapsed, 2))

            # Graceful degradation — return heuristic result
            return self._heuristic_fallback(raw_input)

    def _heuristic_fallback(self, raw_input: str) -> IntentExtractionResult:
        """
        Rule-based fallback when LLM call fails.
        Provides a best-effort intent extraction using simple heuristics.
        """
        words = raw_input.strip().split()
        is_question = raw_input.strip().endswith("?") or raw_input.lower().startswith(
            ("what", "how", "why", "when", "where", "who", "which", "can", "could", "should")
        )

        signal_type = "question" if is_question else "command"
        signals = [IntentSignal(type=signal_type, weight=0.7)]

        return IntentExtractionResult(
            raw_input=raw_input,
            core_intent=f"User wants to: {raw_input[:100]}",
            sub_intents=[],
            signals=signals,
            domain_hints=[],
            confidence=0.3,
            ambiguity_level=AmbiguityLevel.MEDIUM,
        )
