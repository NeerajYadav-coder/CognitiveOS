"""
Cognitive Pipeline Orchestrator — CognitiveOS
The master orchestrator that sequences all cognitive engines.
Coordinates: Intent → Mode → Ambiguity → Vocabulary → Thought → Synthesis
"""
from __future__ import annotations

import asyncio
import time
import uuid
from typing import Optional

import structlog

from src.config.settings import get_settings
from src.schemas.cognitive import (
    CognitivePipelineResponse,
    PipelineStageResult,
    ProcessCognitiveRequest,
    SynthesizedPrompt,
)
from src.services.intent_engine import IntentEngine
from src.services.mode_detector import ModeDetector
from src.services.ambiguity_analyzer import AmbiguityAnalyzer
from src.services.vocabulary_engine import VocabularyEngine
from src.services.thought_structurer import ThoughtStructurer
from src.services.prompt_synthesizer import PromptSynthesizer

logger = structlog.get_logger(__name__)
settings = get_settings()


class CognitivePipelineOrchestrator:
    """
    The master orchestrator for the CognitiveOS cognitive pipeline.

    Sequences all engines in the correct order, handles failures gracefully,
    collects stage results and timing, and returns a complete pipeline response.

    Architecture:
        Raw Input
            → Intent Engine           (extract intent structure)
            → Mode Detector           (classify cognitive mode)
            → Ambiguity Analyzer      (surface vagueness, generate questions)
            → Vocabulary Engine       (expand lexical resources)
            → Thought Structurer      (apply cognitive framework)
            → Prompt Synthesizer      (construct final optimized prompt)
    """

    def __init__(self) -> None:
        self._intent_engine = IntentEngine()
        self._mode_detector = ModeDetector()
        self._ambiguity_analyzer = AmbiguityAnalyzer()
        self._vocabulary_engine = VocabularyEngine()
        self._thought_structurer = ThoughtStructurer()
        self._prompt_synthesizer = PromptSynthesizer()
        self._log = logger.bind(component="pipeline-orchestrator")

    async def process(
        self,
        request: ProcessCognitiveRequest,
    ) -> CognitivePipelineResponse:
        """
        Execute the full cognitive pipeline for a given user input.

        Args:
            request: ProcessCognitiveRequest with raw_input and context

        Returns:
            CognitivePipelineResponse with all stage results and final output
        """
        pipeline_start = time.perf_counter()
        request_id = str(uuid.uuid4())
        session_id = request.session_id or str(uuid.uuid4())
        stages: list[PipelineStageResult] = []

        log = self._log.bind(
            request_id=request_id,
            session_id=session_id,
            input_length=len(request.raw_input),
        )
        log.info("Starting cognitive pipeline")

        # ── Stage 1: Intent Extraction ──────────────────────────
        stage_start = time.perf_counter()
        try:
            intent_result = await self._intent_engine.extract(
                raw_input=request.raw_input,
                session_id=session_id,
            )
            stages.append(PipelineStageResult(
                stage="intent-extraction",
                status="completed",
                processing_time_ms=(time.perf_counter() - stage_start) * 1000,
                data=intent_result.model_dump(),
            ))
            log.info("Stage 1 complete: Intent Extraction")
        except Exception as e:
            stages.append(self._failed_stage("intent-extraction", stage_start, str(e)))
            log.error("Stage 1 failed: Intent Extraction", error=str(e))
            return self._error_response(request_id, session_id, stages, pipeline_start)

        # ── Stage 2: Cognitive Mode Detection ──────────────────
        stage_start = time.perf_counter()
        try:
            mode_result = await self._mode_detector.detect(
                intent_result=intent_result,
                session_id=session_id,
            )
            stages.append(PipelineStageResult(
                stage="mode-detection",
                status="completed",
                processing_time_ms=(time.perf_counter() - stage_start) * 1000,
                data=mode_result.model_dump(),
            ))
            log.info("Stage 2 complete: Mode Detection", mode=mode_result.primary.value)
        except Exception as e:
            stages.append(self._failed_stage("mode-detection", stage_start, str(e)))
            log.error("Stage 2 failed: Mode Detection", error=str(e))

        # ── Stage 3: Ambiguity Analysis ─────────────────────────
        stage_start = time.perf_counter()
        skip_ambiguity = (
            request.user_preferences
            and request.user_preferences.skip_ambiguity_check
        )

        if skip_ambiguity:
            stages.append(PipelineStageResult(
                stage="ambiguity-analysis",
                status="skipped",
                processing_time_ms=0,
                data=None,
            ))
            from src.schemas.cognitive import AmbiguityAnalysis, AmbiguityLevel
            ambiguity_result = AmbiguityAnalysis(
                level=AmbiguityLevel.LOW,
                score=10.0,
                can_proceed_without_clarification=True,
            )
        else:
            try:
                ambiguity_result = await self._ambiguity_analyzer.analyze(
                    intent_result=intent_result,
                    mode_result=mode_result,
                    session_id=session_id,
                )
                stages.append(PipelineStageResult(
                    stage="ambiguity-analysis",
                    status="completed",
                    processing_time_ms=(time.perf_counter() - stage_start) * 1000,
                    data=ambiguity_result.model_dump(),
                ))
                log.info("Stage 3 complete: Ambiguity Analysis", level=ambiguity_result.level.value)
            except Exception as e:
                stages.append(self._failed_stage("ambiguity-analysis", stage_start, str(e)))
                log.error("Stage 3 failed: Ambiguity Analysis", error=str(e))
                from src.schemas.cognitive import AmbiguityAnalysis, AmbiguityLevel
                ambiguity_result = AmbiguityAnalysis(
                    level=AmbiguityLevel.UNKNOWN if hasattr(AmbiguityLevel, 'UNKNOWN') else AmbiguityLevel.MEDIUM,
                    score=50.0,
                    can_proceed_without_clarification=True,
                )

        # ── Stage 4: Vocabulary Expansion ──────────────────────
        stage_start = time.perf_counter()
        try:
            vocab_result = await self._vocabulary_engine.expand(
                intent_result=intent_result,
                mode_result=mode_result,
                session_id=session_id,
            )
            stages.append(PipelineStageResult(
                stage="vocabulary-expansion",
                status="completed",
                processing_time_ms=(time.perf_counter() - stage_start) * 1000,
                data=vocab_result.model_dump(),
            ))
            log.info("Stage 4 complete: Vocabulary Expansion")
        except Exception as e:
            stages.append(self._failed_stage("vocabulary-expansion", stage_start, str(e)))
            log.error("Stage 4 failed: Vocabulary Expansion", error=str(e))
            from src.schemas.cognitive import VocabularyExpansion
            vocab_result = VocabularyExpansion(
                original_terms=[], domain_terminology=[], expanded_vocabulary=[], conceptual_synonyms={}
            )

        # ── Stage 5: Thought Structuring ────────────────────────
        stage_start = time.perf_counter()
        vocab_highlights = [v.term for v in vocab_result.expanded_vocabulary[:5]]
        try:
            thought_structure = await self._thought_structurer.structure(
                intent_result=intent_result,
                mode_result=mode_result,
                vocab_highlights=vocab_highlights,
                session_id=session_id,
            )
            stages.append(PipelineStageResult(
                stage="thought-structuring",
                status="completed",
                processing_time_ms=(time.perf_counter() - stage_start) * 1000,
                data=thought_structure.model_dump(),
            ))
            log.info("Stage 5 complete: Thought Structuring", framework=thought_structure.framework.value)
        except Exception as e:
            stages.append(self._failed_stage("thought-structuring", stage_start, str(e)))
            log.error("Stage 5 failed: Thought Structuring", error=str(e))
            thought_structure = self._thought_structurer._minimal_fallback(
                intent_result, None  # type: ignore
            )

        # ── Stage 6: Prompt Synthesis ───────────────────────────
        stage_start = time.perf_counter()
        try:
            final_output = await self._prompt_synthesizer.synthesize(
                intent_result=intent_result,
                mode_result=mode_result,
                ambiguity_result=ambiguity_result,
                vocab_result=vocab_result,
                thought_structure=thought_structure,
                session_id=session_id,
            )
            stages.append(PipelineStageResult(
                stage="prompt-synthesis",
                status="completed",
                processing_time_ms=(time.perf_counter() - stage_start) * 1000,
                data=final_output.model_dump(),
            ))
            log.info("Stage 6 complete: Prompt Synthesis", quality=final_output.metadata.quality_score)
        except Exception as e:
            stages.append(self._failed_stage("prompt-synthesis", stage_start, str(e)))
            log.error("Stage 6 failed: Prompt Synthesis", error=str(e))
            final_output = self._prompt_synthesizer._direct_synthesis(
                intent_result, ambiguity_result, thought_structure
            )

        total_time = (time.perf_counter() - pipeline_start) * 1000
        log.info(
            "Cognitive pipeline complete",
            total_stages=len(stages),
            total_ms=round(total_time, 2),
            quality_score=final_output.metadata.quality_score,
        )

        return CognitivePipelineResponse(
            session_id=session_id,
            request_id=request_id,
            stages=stages,
            final_output=final_output,
            total_processing_time_ms=round(total_time, 2),
        )

    def _failed_stage(
        self, stage_name: str, start: float, error: str
    ) -> PipelineStageResult:
        return PipelineStageResult(
            stage=stage_name,
            status="failed",
            processing_time_ms=(time.perf_counter() - start) * 1000,
            data=None,
            error=error,
        )

    def _error_response(
        self,
        request_id: str,
        session_id: str,
        stages: list[PipelineStageResult],
        pipeline_start: float,
    ) -> CognitivePipelineResponse:
        """Returns a minimal error response when the pipeline cannot continue."""
        from src.schemas.cognitive import (
            SynthesizedPrompt, PromptMetadata, CognitiveMode, ThoughtFramework
        )
        error_output = SynthesizedPrompt(
            final_prompt="Pipeline encountered a critical error. Please try again.",
            system_context="",
            user_message="",
            metadata=PromptMetadata(
                word_count=0,
                estimated_tokens=0,
                cognitive_mode=CognitiveMode.UNKNOWN,
                framework=ThoughtFramework.CHAIN_OF_THOUGHT,
                ambiguity_score=0,
                quality_score=0,
            ),
        )
        return CognitivePipelineResponse(
            session_id=session_id,
            request_id=request_id,
            stages=stages,
            final_output=error_output,
            total_processing_time_ms=(time.perf_counter() - pipeline_start) * 1000,
        )
