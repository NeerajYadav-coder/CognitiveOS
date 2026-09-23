import asyncio
import json
from typing import Optional, Dict, Any

from openai import AsyncOpenAI
from src.config.settings import get_settings
from src.schemas.cognitive import (
    CognitiveReflection,
    ReflectionSummary,
    CognitiveMemory,
    IntentExtraction,
    CognitiveMode,
    ThoughtStructure
)
from src.services.reflection.taxonomy import ReflectionCategory
from src.services.reflection.heuristics import protect_against_diagnosis, reframe_blind_spots
from src.services.reflection.prompts import REFLECTION_SYSTEM_PROMPT, REFLECTION_USER_PROMPT
from src.utils.logger import logger

settings = get_settings()

class ReflectionLLMService:
    """
    Abstracts LLM communication for the Cognitive Reflection Engine.
    Generates meta-cognitive insights to help the user understand their thinking.
    """
    def __init__(self, client: Optional[AsyncOpenAI] = None):
        self._client = client or AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY, 
            base_url=settings.OPENAI_API_BASE
        )
    
    async def process_reflection(
        self, 
        raw_input: str,
        intent: Optional[IntentExtraction],
        mode: Optional[CognitiveMode],
        thought: Optional[ThoughtStructure],
        memory: Optional[CognitiveMemory]
    ) -> CognitiveReflection:
        
        logger.info("Calling REAL LLM for Meta-Cognitive Reflection...")
        
        system = REFLECTION_SYSTEM_PROMPT
        user = REFLECTION_USER_PROMPT.format(
            intent=intent.model_dump_json(indent=2) if intent else "None",
            mode=mode.model_dump_json(indent=2) if mode else "None",
            structure=thought.model_dump_json(indent=2) if thought else "None",
            memory=memory.model_dump_json(indent=2) if memory else "None"
        )
        
        try:
            response = await self._client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            final_text = response.choices[0].message.content.strip()
            final_text = final_text.replace("```json", "").replace("```", "").strip()
            data = json.loads(final_text)
            
            summary_data = data.get("reflection_summary", {})
            summary = ReflectionSummary(
                dominant_themes=summary_data.get("dominant_themes", []),
                emerging_interests=summary_data.get("emerging_interests", []),
                cognitive_shifts=summary_data.get("cognitive_shifts", []),
                reasoning_patterns=summary_data.get("reasoning_patterns", []),
                exploration_trends=summary_data.get("exploration_trends", [])
            )
            
            reflection = CognitiveReflection(
                reflection_summary=summary,
                possible_blind_spots=data.get("possible_blind_spots", []),
                growth_signals=data.get("growth_signals", []),
                confidence=float(data.get("confidence", 0.85))
            )
            
        except Exception as e:
            logger.warning(f"REAL LLM Reflection parsing failed: {str(e)}. Falling back to heuristics.")
            
            # Heuristic Fallback
            if mode and "philosophical" in [m.name for m in mode.modes]:
                summary = ReflectionSummary(
                    dominant_themes=["Existential inquiry", "Meaning-making"],
                    emerging_interests=["Sociology", "Psychology of alienation"],
                    cognitive_shifts=["Moving from tactical problem-solving to abstract philosophy"],
                    reasoning_patterns=["Socratic questioning", "Dialectical reasoning"],
                    exploration_trends=["Increasing depth of abstract thought"]
                )
                blind_spots = ["User ignores the biological components of emotion"]
                growth = ["High intellectual courage", "Willingness to explore ambiguity"]
            else:
                summary = ReflectionSummary(
                    dominant_themes=["Systems Architecture", "Optimization"],
                    emerging_interests=["Data orchestration"],
                    cognitive_shifts=["Transitioning from isolated scripts to systems thinking"],
                    reasoning_patterns=["First-principles decomposition"],
                    exploration_trends=["Highly structured analytical deep-dives"]
                )
                blind_spots = ["User lacks exploration of non-technical UX considerations"]
                growth = ["Increasing structural rigor"]

            reflection = CognitiveReflection(
                reflection_summary=summary,
                possible_blind_spots=blind_spots,
                growth_signals=growth,
                confidence=0.8
            )
        
        # Apply Defensive Heuristics
        reflection = protect_against_diagnosis(reflection)
        reflection = reframe_blind_spots(reflection)
        
        return reflection
