from abc import ABC, abstractmethod
from typing import Any, Optional, Dict
import time
import logging

from src.schemas.cognitive import CognitiveState, EngineResult, CognitiveMetadata
from src.utils.logger import logger
from src.utils.exceptions import EngineProcessingError

class BaseCognitiveEngine(ABC):
    """
    Abstract base class for all Cognitive Engines.
    Enforces a strict interface for processing the CognitiveState.
    """
    
    @property
    @abstractmethod
    def engine_name(self) -> str:
        """Unique name of the engine."""
        pass
    
    @property
    def requires_llm(self) -> bool:
        """Does this engine require an external LLM call?"""
        return False
        
    async def execute(self, state: CognitiveState, **kwargs) -> CognitiveState:
        """
        Executes the engine logic, measures performance, and appends the result to the state.
        Do NOT override this method directly. Override `process`.
        """
        start_time = time.time()
        result = EngineResult(engine_name=self.engine_name, status="processing")
        
        try:
            logger.info(f"[{self.engine_name}] Starting execution", extra={"session_id": state.session_id})
            
            # Subclasses implement the actual logic in `process`
            output, metadata_updates = await self.process(state, **kwargs)
            
            processing_time = (time.time() - start_time) * 1000
            
            # Update State
            self._update_state_with_output(state, output)
            
            result.status = "success"
            result.output = output
            result.metadata.processing_time_ms = processing_time
            if metadata_updates:
                for k, v in metadata_updates.items():
                    setattr(result.metadata, k, v)
                    
            logger.info(f"[{self.engine_name}] Execution successful", extra={"processing_time_ms": processing_time})
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            result.status = "failed"
            result.error = str(e)
            result.metadata.processing_time_ms = processing_time
            logger.error(f"[{self.engine_name}] Execution failed: {e}", exc_info=True)
            raise EngineProcessingError(f"Engine {self.engine_name} failed: {e}", engine_name=self.engine_name)
        finally:
            state.add_result(result)
            
        return state

    @abstractmethod
    async def process(self, state: CognitiveState, **kwargs) -> tuple[Any, Optional[Dict[str, Any]]]:
        """
        Core processing logic for the engine.
        Should return the resulting Pydantic object and an optional dictionary of metadata updates.
        """
        pass

    @abstractmethod
    def _update_state_with_output(self, state: CognitiveState, output: Any):
        """
        Mutates the CognitiveState safely with the typed output.
        """
        pass
