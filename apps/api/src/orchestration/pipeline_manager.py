import asyncio
from typing import List, Type
from src.schemas.cognitive import CognitiveState
from src.pipelines.base import BaseCognitiveEngine
from src.utils.logger import logger
from src.utils.exceptions import EngineProcessingError

class CognitivePipeline:
    """
    Orchestrates the sequential execution of Cognitive Engines.
    Handles retry logic, circuit breaking, and global observability.
    """
    def __init__(self, name: str, engines: List[BaseCognitiveEngine]):
        self.name = name
        self.engines = engines

    async def _execute_engine_with_retry(self, engine: BaseCognitiveEngine, state: CognitiveState, max_retries: int = 3) -> CognitiveState:
        """Executes a single engine with exponential backoff retry logic."""
        attempt = 0
        while attempt < max_retries:
            try:
                return await engine.execute(state)
            except EngineProcessingError as e:
                attempt += 1
                logger.warning(
                    f"[{self.name}] Engine {engine.engine_name} failed (Attempt {attempt}/{max_retries}).", 
                    extra={"error": str(e)}
                )
                if attempt >= max_retries:
                    logger.error(f"[{self.name}] Engine {engine.engine_name} exhausted retries.")
                    raise e
                await asyncio.sleep(2 ** attempt) # Exponential backoff
            except Exception as e:
                # Do not retry on unknown critical errors
                logger.error(f"[{self.name}] Critical unhandled error in {engine.engine_name}: {e}")
                raise e

    async def run(self, state: CognitiveState) -> CognitiveState:
        """
        Runs the full pipeline dynamically, utilizing orchestration routing to skip or execute engines.
        """
        logger.info(f"[{self.name}] Starting adaptive pipeline execution for session {state.session_id}")
        
        from src.services.orchestration.heuristics import route_next_engines
        from src.schemas.cognitive import OrchestrationState, ExecutionPlan
        
        # Initialize Orchestration State
        all_engines = [e.engine_name for e in self.engines]
        state.orchestration = OrchestrationState(
            execution_plan=ExecutionPlan(pipeline=all_engines),
            confidence=1.0
        )
        
        for idx, engine in enumerate(self.engines):
            state.orchestration.current_engine_index = idx
            
            # Dynamic routing decision for the remaining engines
            remaining_engines = [e.engine_name for e in self.engines[idx:]]
            decisions = route_next_engines(state, remaining_engines)
            
            # Find the decision for the current engine
            current_decision = next((d for d in decisions if d.engine_name == engine.engine_name), None)
            
            if current_decision and current_decision.action == "skip":
                logger.info(f"[{self.name}] Skipping {engine.engine_name}: {current_decision.reason}")
                state.orchestration.execution_plan.routing_decisions.append(current_decision)
                
                from src.schemas.cognitive import EngineResult, CognitiveMetadata
                state.add_result(EngineResult(
                    engine_name=engine.engine_name,
                    status="skipped",
                    metadata=CognitiveMetadata(processing_time_ms=0)
                ))
                continue
            
            # Execute engine if not skipped
            state = await self._execute_engine_with_retry(engine, state)
            
        logger.info(f"[{self.name}] Pipeline execution completed for session {state.session_id}")
        return state
