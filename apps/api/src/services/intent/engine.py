import json
from typing import Any, Dict, Optional
import asyncio

from openai import AsyncOpenAI
from src.config.settings import get_settings
from src.schemas.cognitive import IntentExtraction
from src.services.intent.prompts import INTENT_EXTRACTION_SYSTEM_PROMPT, INTENT_EXTRACTION_USER_PROMPT
from src.services.intent.scoring import calculate_confidence, validate_intent
from src.utils.logger import logger
from src.utils.exceptions import EngineProcessingError

settings = get_settings()

class IntentLLMService:
    """
    Direct LLM communication for intent extraction.
    Utilizes AsyncOpenAI for structured intent parsing with fallback logic.
    """
    
    def __init__(self, client: Optional[AsyncOpenAI] = None):
        self._client = client or AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY, 
            base_url=settings.OPENAI_API_BASE
        )
        
    async def extract_intent(self, raw_input: str) -> IntentExtraction:
        logger.info("Calling REAL LLM for Intent Extraction...")
        system = INTENT_EXTRACTION_SYSTEM_PROMPT
        user = INTENT_EXTRACTION_USER_PROMPT.format(raw_input=raw_input)
        
        try:
            response = await self._client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            final_text = response.choices[0].message.content.strip()
            final_text = final_text.replace("```json", "").replace("```", "").strip()
            data = json.loads(final_text)
            
            intent_extracted = IntentExtraction(
                primary_intent=data.get("primary_intent", "Unknown"),
                secondary_intents=data.get("secondary_intents", []),
                domain=data.get("domain", "General"),
                depth_level=data.get("depth_level", "intermediate"),
                confidence=float(data.get("confidence", 0.9))
            )
            
            # Scoring & Validation
            intent_extracted.confidence = calculate_confidence(raw_input, intent_extracted)
            return intent_extracted
            
        except Exception as e:
            logger.warning(f"REAL LLM Intent Extraction failed: {str(e)}. Falling back to heuristics.")
            
            # Heuristic Fallback
            if "angry" in raw_input.lower() or "hate" in raw_input.lower():
                primary = "Expressing frustration, seeking immediate resolution."
                depth = "surface"
            elif "why" in raw_input.lower() or "how" in raw_input.lower():
                primary = "Understanding core concepts and mechanisms."
                depth = "first_principles"
            else:
                primary = "General information retrieval and task execution."
                depth = "intermediate"

            mock_response = IntentExtraction(
                primary_intent=primary,
                secondary_intents=["Identify root cause", "Suggest improvements"],
                domain="Software Engineering",
                depth_level=depth,
                confidence=0.9
            )
            mock_response.confidence = calculate_confidence(raw_input, mock_response)
            return mock_response
