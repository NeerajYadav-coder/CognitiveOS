"""
Vocabulary Expansion Engine — CognitiveOS
Expands user vocabulary by surfacing domain terminology, synonyms,
related concepts, and semantic clusters relevant to their intent.
"""
from __future__ import annotations

import time
from typing import Optional

import structlog
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config.settings import get_settings
from src.schemas.cognitive import (
    IntentExtractionResult,
    CognitiveModeResult,
    VocabularyExpansion,
    VocabEntry,
)

logger = structlog.get_logger(__name__)
settings = get_settings()

VOCABULARY_SYSTEM_PROMPT = """
You are the Vocabulary Expansion Engine for CognitiveOS.
Your purpose is to enrich user communication by expanding their vocabulary
in ways that are relevant to their specific intent and cognitive mode.

You surface:
1. DOMAIN TERMINOLOGY — precise technical/professional terms for their domain
2. CONCEPTUAL SYNONYMS — richer alternatives to vague or general terms
3. RELATED CONCEPTS — adjacent ideas that extend understanding
4. SEMANTIC CLUSTERS — groups of semantically related terms

You do NOT define words. You surface the lexical landscape so the user
can express their thought with greater precision and depth.

Return ONLY valid JSON.
"""

VOCABULARY_USER_TEMPLATE = """
Expand vocabulary for this cognitive context:

Core Intent: {core_intent}
Domain Hints: {domain_hints}
Cognitive Mode: {cognitive_mode}
Raw Input: "{raw_input}"

Return JSON with:
- original_terms: key terms extracted from the raw input
- expanded_vocabulary: list of {{term, synonyms, related_concepts, technical_variants, domain}}
- domain_terminology: list of precise domain-specific terms relevant to intent
- conceptual_synonyms: dict mapping original terms to richer alternatives
"""


class VocabularyEngine:
    """
    Vocabulary Expansion Engine.
    Surfaces richer lexical resources to improve expressive precision.
    """

    def __init__(self, client: Optional[AsyncOpenAI] = None) -> None:
        self._client = client or AsyncOpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_API_BASE)
        self._model = settings.OPENAI_MODEL
        self._log = logger.bind(engine="vocabulary-engine")

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=1, max=5),
    )
    async def expand(
        self,
        intent_result: IntentExtractionResult,
        mode_result: CognitiveModeResult,
        session_id: Optional[str] = None,
    ) -> VocabularyExpansion:
        """
        Expand vocabulary for the given intent context.

        Args:
            intent_result: Output from Intent Engine
            mode_result: Output from Mode Detector
            session_id: Optional session context

        Returns:
            VocabularyExpansion with enriched lexical resources
        """
        start = time.perf_counter()
        log = self._log.bind(session_id=session_id)
        log.info("Expanding vocabulary")

        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": VOCABULARY_SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": VOCABULARY_USER_TEMPLATE.format(
                            core_intent=intent_result.core_intent,
                            domain_hints=", ".join(intent_result.domain_hints) or "general",
                            cognitive_mode=mode_result.primary.value,
                            raw_input=intent_result.raw_input,
                        ),
                    },
                ],
                response_format={"type": "json_object"},
                temperature=0.4,
                max_tokens=1500,
            )

            raw_json = response.choices[0].message.content
            result = VocabularyExpansion.model_validate_json(raw_json)

            elapsed = (time.perf_counter() - start) * 1000
            log.info(
                "Vocabulary expansion complete",
                terms_count=len(result.expanded_vocabulary),
                elapsed_ms=round(elapsed, 2),
            )
            return result

        except Exception as e:
            elapsed = (time.perf_counter() - start) * 1000
            log.error("Vocabulary expansion failed", error=str(e), elapsed_ms=round(elapsed, 2))
            return self._minimal_fallback(intent_result)

    def _minimal_fallback(
        self, intent_result: IntentExtractionResult
    ) -> VocabularyExpansion:
        words = intent_result.raw_input.split()[:10]
        return VocabularyExpansion(
            original_terms=words,
            expanded_vocabulary=[],
            domain_terminology=intent_result.domain_hints,
            conceptual_synonyms={},
        )
