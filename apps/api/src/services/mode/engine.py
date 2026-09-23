import asyncio
import json
from typing import Optional, List
from openai import AsyncOpenAI
from src.config.settings import get_settings

from src.schemas.cognitive import CognitiveMode, ModeScore, IntentExtraction
from src.services.mode.prompts import MODE_DETECTION_SYSTEM_PROMPT, MODE_DETECTION_USER_PROMPT
from src.services.mode.heuristics import generate_heuristic_baseline, merge_and_normalize_scores, determine_primary_mode
from src.utils.logger import logger
from src.utils.exceptions import EngineProcessingError

settings = get_settings()

class ModeLLMService:
    """
    Direct LLM communication for Cognitive Mode Detection.
    Executes a multi-label classification pipeline blending ML + Heuristics.
    """
    
    def __init__(self, client: Optional[AsyncOpenAI] = None):
        self._client = client or AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY, 
            base_url=settings.OPENAI_API_BASE
        )
        
    async def detect_mode(self, raw_input: str, intent: Optional[IntentExtraction]) -> CognitiveMode:
        intent_summary = intent.primary_intent if intent else "Unknown"
        
        logger.info("Calling REAL LLM for Mode Detection...")
        
        # 1. Generate Heuristic Baseline
        baseline_scores = generate_heuristic_baseline(raw_input)
        
        llm_output: List[ModeScore] = []
        try:
            response = await self._client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": MODE_DETECTION_SYSTEM_PROMPT},
                    {"role": "user", "content": MODE_DETECTION_USER_PROMPT.format(intent_summary=intent_summary, raw_input=raw_input)}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            final_text = response.choices[0].message.content.strip()
            final_text = final_text.replace("```json", "").replace("```", "").strip()
            data = json.loads(final_text)
            
            modes_data = data.get("modes", [])
            if isinstance(modes_data, list):
                for m in modes_data:
                    llm_output.append(ModeScore(name=m.get("name"), score=float(m.get("score", 0.5))))
            elif isinstance(modes_data, dict):
                for k, v in modes_data.items():
                    llm_output.append(ModeScore(name=k, score=float(v)))
                    
        except Exception as e:
            logger.warning(f"REAL LLM Mode Detection failed: {str(e)}. Falling back to heuristics.")
            
            raw_lower = raw_input.lower()
            if "bug" in raw_lower or "error" in raw_lower:
                llm_output.append(ModeScore(name="technical", score=0.9))
                if "fuck" in raw_lower or "hate" in raw_lower:
                    llm_output.append(ModeScore(name="emotional", score=0.75))
            elif "why" in raw_lower and "meaning" in raw_lower:
                llm_output.append(ModeScore(name="philosophical", score=0.85))
                llm_output.append(ModeScore(name="exploratory", score=0.6))
            else:
                llm_output.append(ModeScore(name="exploratory", score=0.8))
                llm_output.append(ModeScore(name="practical", score=0.5))
                
        # 3. Merge Heuristics and ML Output to prevent hallucination/overfitting
        merged_scores = merge_and_normalize_scores(llm_output, baseline_scores)
        primary = determine_primary_mode(merged_scores)
        
        # Calculate overall confidence (average of top 2 modes' blended scores)
        top_scores = [m.score for m in merged_scores[:2]]
        confidence = sum(top_scores) / len(top_scores) if top_scores else 0.5
        
        return CognitiveMode(
            modes=merged_scores,
            primary_mode=primary,
            confidence=round(confidence, 2)
        )
