"""
Prompt Synthesis Engine — CognitiveOS
Constructs the final, optimized prompt from all pipeline stage outputs.
This is the culmination of the cognitive pipeline — synthesizing intent,
mode, structure, and vocabulary into a precise, effective LLM interaction.
"""
from __future__ import annotations

import time
from typing import Optional
import tiktoken

import structlog
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config.settings import get_settings
from src.schemas.cognitive import (
    AmbiguityAnalysis,
    CognitiveModeResult,
    IntentExtractionResult,
    PromptMetadata,
    SynthesizedPrompt,
    ThoughtStructure,
    VocabularyExpansion,
)

logger = structlog.get_logger(__name__)
settings = get_settings()

SYNTHESIS_SYSTEM_PROMPT = """
You are the Prompt Synthesis Engine for CognitiveOS.
Your role is to construct the FINAL, OPTIMAL prompt that a human will use 
to interact with an AI system.

You synthesize:
- The user's core intent and sub-intents
- The detected cognitive mode
- The structured thinking framework
- The expanded vocabulary
- The resolved ambiguities

The final prompt must:
1. Be clear, specific, and unambiguous
2. Leverage domain vocabulary appropriately
3. Follow the chosen thinking framework
4. Include necessary context without being verbose
5. Guide the AI toward the most useful response format

Also generate:
- A SYSTEM CONTEXT that primes the AI for this specific type of interaction
- 2 ALTERNATIVE phrasings for user to choose from

Return ONLY valid JSON.
"""

SYNTHESIS_USER_TEMPLATE = """
Synthesize the final prompt from these pipeline outputs:

=== INTENT ===
Core Intent: {core_intent}
Sub-Intents: {sub_intents}

=== COGNITIVE MODE ===
Primary: {cognitive_mode}
Reasoning: {mode_reasoning}

=== THOUGHT STRUCTURE ===
Framework: {framework}
Sections:
{sections_text}
Logical Flow: {logical_flow}
Output Format: {output_format}

=== VOCABULARY ===
Domain Terms: {domain_terms}
Key Concepts: {key_concepts}

=== AMBIGUITY STATUS ===
Level: {ambiguity_level}
Resolved: {can_proceed}

=== ORIGINAL INPUT ===
"{raw_input}"

Return JSON with:
- final_prompt: the complete, optimized prompt string
- system_context: a brief system message to prime the AI
- user_message: the user turn of the conversation
- metadata: {{word_count, estimated_tokens, cognitive_mode, framework, ambiguity_score, quality_score}}
- alternatives: list of 2 alternative prompt formulations
"""


class PromptSynthesizer:
    """
    Prompt Synthesis Engine.
    Constructs the final optimized prompt from all pipeline stage outputs.
    """

    def __init__(self, client: Optional[AsyncOpenAI] = None) -> None:
        self._client = client or AsyncOpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_API_BASE)
        self._model = settings.OPENAI_MODEL
        self._log = logger.bind(engine="prompt-synthesizer")
        try:
            self._encoder = tiktoken.encoding_for_model("gpt-4o")
        except Exception:
            self._encoder = None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
    )
    async def synthesize(
        self,
        intent_result: IntentExtractionResult,
        mode_result: CognitiveModeResult,
        ambiguity_result: AmbiguityAnalysis,
        vocab_result: VocabularyExpansion,
        thought_structure: ThoughtStructure,
        session_id: Optional[str] = None,
    ) -> SynthesizedPrompt:
        """
        Synthesize final prompt from all pipeline outputs.

        Returns:
            SynthesizedPrompt with final_prompt, system_context, metadata
        """
        start = time.perf_counter()
        log = self._log.bind(session_id=session_id)
        log.info("Synthesizing final prompt")

        sections_text = "\n".join(
            [f"  [{s.title}] (weight={s.weight}): {s.content}" for s in thought_structure.sections]
        )
        domain_terms = ", ".join(vocab_result.domain_terminology[:10])
        key_concepts = ", ".join(
            [v.term for v in vocab_result.expanded_vocabulary[:5]]
        )

        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": SYNTHESIS_SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": SYNTHESIS_USER_TEMPLATE.format(
                            core_intent=intent_result.core_intent,
                            sub_intents=", ".join(intent_result.sub_intents) or "none",
                            cognitive_mode=mode_result.primary.value,
                            mode_reasoning=mode_result.reasoning,
                            framework=thought_structure.framework.value,
                            sections_text=sections_text,
                            logical_flow=" → ".join(thought_structure.logical_flow),
                            output_format=thought_structure.output_format,
                            domain_terms=domain_terms or "general",
                            key_concepts=key_concepts or "none",
                            ambiguity_level=ambiguity_result.level.value,
                            can_proceed=ambiguity_result.can_proceed_without_clarification,
                            raw_input=intent_result.raw_input,
                        ),
                    },
                ],
                response_format={"type": "json_object"},
                temperature=0.5,
                max_tokens=2500,
            )

            raw_json = response.choices[0].message.content
            result = SynthesizedPrompt.model_validate_json(raw_json)

            elapsed = (time.perf_counter() - start) * 1000
            log.info(
                "Prompt synthesis complete",
                quality_score=result.metadata.quality_score,
                token_estimate=result.metadata.estimated_tokens,
                elapsed_ms=round(elapsed, 2),
            )
            return result

        except Exception as e:
            elapsed = (time.perf_counter() - start) * 1000
            log.error("Prompt synthesis failed", error=str(e), elapsed_ms=round(elapsed, 2))
            return self._direct_synthesis(intent_result, ambiguity_result, thought_structure)

    def _estimate_tokens(self, text: str) -> int:
        if self._encoder:
            return len(self._encoder.encode(text))
        return len(text.split()) * 4 // 3

    def _direct_synthesis(
        self,
        intent_result: IntentExtractionResult,
        ambiguity_result: AmbiguityAnalysis,
        thought_structure: ThoughtStructure,
    ) -> SynthesizedPrompt:
        """Direct assembly fallback without LLM."""
        sections_text = "\n\n".join(
            [f"## {s.title}\n{s.content}" for s in thought_structure.sections]
        )
        final_prompt = f"{intent_result.core_intent}\n\n{sections_text}"

        return SynthesizedPrompt(
            final_prompt=final_prompt,
            system_context="You are a helpful AI assistant.",
            user_message=final_prompt,
            metadata=PromptMetadata(
                word_count=len(final_prompt.split()),
                estimated_tokens=self._estimate_tokens(final_prompt),
                cognitive_mode=intent_result.ambiguity_level.value,  # type: ignore
                framework=thought_structure.framework,
                ambiguity_score=ambiguity_result.score,
                quality_score=40.0,
            ),
            alternatives=[intent_result.raw_input],
        )
