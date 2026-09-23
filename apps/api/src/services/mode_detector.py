"""
Cognitive Mode Detector — CognitiveOS
Classifies the cognitive mode of user thinking based on intent signals,
linguistic patterns, and domain context.
"""
from __future__ import annotations

import time
from typing import List, Optional

import structlog
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config.settings import get_settings
from src.schemas.cognitive import (
    CognitiveMode,
    CognitiveModeResult,
    IntentExtractionResult,
)

logger = structlog.get_logger(__name__)
settings = get_settings()

MODE_DETECTION_SYSTEM_PROMPT = """
You are the Cognitive Mode Detector for CognitiveOS.
Your role is to classify the PRIMARY cognitive mode a human is operating in 
based on their intent extraction data.

Cognitive Modes:
- exploratory: Open-ended curiosity, divergent thinking, "I wonder..." style
- analytical: Breaking down problems, structured reasoning, systematic inquiry
- creative: Generative, metaphorical, associative, seeking novelty
- critical: Evaluating claims, debating, questioning assumptions, skeptical
- synthetic: Integrating ideas across domains, seeking unified understanding
- procedural: Step-by-step guidance, task-focused, how-to oriented
- reflective: Introspective, metacognitive, thinking about thinking
- unknown: Cannot determine with confidence

Identify the PRIMARY mode and optionally a SECONDARY mode.
Explain your reasoning and list observable signals.
Return ONLY valid JSON.
"""

MODE_DETECTION_USER_TEMPLATE = """
Classify the cognitive mode from this intent extraction result:

Core Intent: {core_intent}
Sub-Intents: {sub_intents}
Signals: {signals}
Domain Hints: {domain_hints}
Ambiguity Level: {ambiguity_level}

Return JSON with:
- primary: one of the cognitive mode values
- secondary: optional secondary mode (or null)
- confidence: 0.0-1.0
- reasoning: one paragraph explanation
- signals: list of observed linguistic/cognitive signals
"""

# Heuristic keyword maps for fallback
MODE_KEYWORDS: dict[CognitiveMode, list[str]] = {
    CognitiveMode.EXPLORATORY: ["explore", "curious", "what if", "wonder", "discover", "learn about"],
    CognitiveMode.ANALYTICAL: ["analyze", "break down", "compare", "examine", "evaluate", "assess"],
    CognitiveMode.CREATIVE: ["create", "imagine", "design", "invent", "brainstorm", "novel"],
    CognitiveMode.CRITICAL: ["critique", "argue", "debate", "flaws", "problems", "challenge"],
    CognitiveMode.SYNTHETIC: ["combine", "integrate", "synthesize", "relate", "connect", "holistic"],
    CognitiveMode.PROCEDURAL: ["how to", "steps", "guide", "tutorial", "process", "implement"],
    CognitiveMode.REFLECTIVE: ["reflect", "think about", "understand myself", "why do i", "what does it mean"],
}


class ModeDetector:
    """
    Cognitive Mode Detector.
    Determines the primary cognitive mode driving the user's inquiry.
    """

    def __init__(self, client: Optional[AsyncOpenAI] = None) -> None:
        self._client = client or AsyncOpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_API_BASE)
        self._model = settings.OPENAI_MODEL
        self._log = logger.bind(engine="mode-detector")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
    )
    async def detect(
        self,
        intent_result: IntentExtractionResult,
        session_id: Optional[str] = None,
    ) -> CognitiveModeResult:
        """
        Detect cognitive mode from intent extraction result.

        Args:
            intent_result: Output from the Intent Engine
            session_id: Optional session context

        Returns:
            CognitiveModeResult with primary mode and confidence
        """
        start = time.perf_counter()
        log = self._log.bind(session_id=session_id)
        log.info("Detecting cognitive mode")

        signals_str = ", ".join(
            [f"{s.type}({s.weight:.1f})" for s in intent_result.signals]
        )

        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": MODE_DETECTION_SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": MODE_DETECTION_USER_TEMPLATE.format(
                            core_intent=intent_result.core_intent,
                            sub_intents=", ".join(intent_result.sub_intents),
                            signals=signals_str,
                            domain_hints=", ".join(intent_result.domain_hints),
                            ambiguity_level=intent_result.ambiguity_level.value,
                        ),
                    },
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                max_tokens=512,
            )

            raw_json = response.choices[0].message.content
            result = CognitiveModeResult.model_validate_json(raw_json)

            elapsed = (time.perf_counter() - start) * 1000
            log.info(
                "Mode detection complete",
                primary_mode=result.primary,
                confidence=result.confidence,
                elapsed_ms=round(elapsed, 2),
            )
            return result

        except Exception as e:
            elapsed = (time.perf_counter() - start) * 1000
            log.error("Mode detection failed", error=str(e), elapsed_ms=round(elapsed, 2))
            return self._heuristic_fallback(intent_result)

    def _heuristic_fallback(
        self, intent_result: IntentExtractionResult
    ) -> CognitiveModeResult:
        """Keyword-based fallback mode detection."""
        text = f"{intent_result.core_intent} {' '.join(intent_result.sub_intents)}".lower()

        best_mode = CognitiveMode.UNKNOWN
        best_score = 0

        for mode, keywords in MODE_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text)
            if score > best_score:
                best_score = score
                best_mode = mode

        return CognitiveModeResult(
            primary=best_mode,
            secondary=None,
            confidence=0.4 if best_score > 0 else 0.1,
            reasoning="Determined via keyword heuristics (LLM fallback).",
            signals=[],
        )
