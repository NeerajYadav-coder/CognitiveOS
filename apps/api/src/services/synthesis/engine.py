import asyncio
import json
from typing import Optional, Dict, Any

from openai import AsyncOpenAI
from src.config.settings import get_settings
from src.schemas.cognitive import (
    PromptSynthesis, 
    PromptStructure, 
    IntentExtraction, 
    CognitiveMode, 
    AmbiguityAnalysis,
    VocabularyExpansion,
    ThoughtStructure,
    UserContext
)
from src.services.synthesis.prompts import SYNTHESIS_SYSTEM_PROMPT, SYNTHESIS_USER_PROMPT
from src.utils.logger import logger

settings = get_settings()

class SynthesisLLMService:
    """
    REAL LLM SERVICE for Prompt Synthesis.
    Converts structured cognition into high-fidelity AI interaction prompts.
    """
    
    def __init__(self, client: Optional[AsyncOpenAI] = None):
        self._client = client or AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY, 
            base_url=settings.OPENAI_API_BASE
        )
    
    async def synthesize_prompt(
        self, 
        raw_input: str, 
        intent: Optional[IntentExtraction], 
        mode: Optional[CognitiveMode],
        ambiguity: Optional[AmbiguityAnalysis],
        vocabulary: Optional[VocabularyExpansion],
        thought: Optional[ThoughtStructure],
        user_context: Optional[UserContext] = None
    ) -> PromptSynthesis:
        
        logger.info("Calling REAL LLM for Prompt Synthesis...")
        
        prof = user_context.profession if user_context else "General User"
        lvl = user_context.intellectual_level if user_context else "intermediate"
        reasoning = "balanced"
        verbosity = "balanced"
        if user_context and user_context.cognitive_style:
            reasoning = user_context.cognitive_style.get("reasoning_preference", "balanced")
            verbosity = user_context.cognitive_style.get("verbosity", "balanced")
            
        domain_list = []
        if user_context and user_context.domain_expertise:
            domain_list = [f"{d.domain} ({d.level})" for d in user_context.domain_expertise]
        domains_str = ", ".join(domain_list) if domain_list else "None"
            
        try:
            # Construct the expert prompt
            user_content = SYNTHESIS_USER_PROMPT.format(
                user_profession=prof or "General User",
                user_level=lvl,
                user_reasoning=reasoning,
                user_verbosity=verbosity,
                user_domains=domains_str,
                intent=intent.primary_intent if intent else "Unknown",
                mode=mode.primary_mode if mode else "Unknown",
                vocabulary=", ".join(vocabulary.recommended_terms) if vocabulary else "None",
                structured_thought=thought.model_dump_json() if thought else "None",
                raw_input=raw_input
            )

            response = await self._client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": SYNTHESIS_SYSTEM_PROMPT},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.4,
                max_tokens=2000
            )

            final_text = response.choices[0].message.content
            
            # CLEANUP: Remove markdown backticks and JSON markers if the LLM added them
            final_text = final_text.replace("```json", "").replace("```", "").strip()
            context = "Expert Synthesis"
            objective = "High-order prompt generation"
            constraints = []
            depth_level = "deep"
            reasoning_style = "Architectural"

            if final_text.startswith("{") and '"final_prompt"' in final_text:
                try:
                    data = json.loads(final_text)
                    final_text = data.get("final_prompt", final_text)
                    structure = data.get("prompt_structure", {})
                    if structure:
                        context = structure.get("context", context)
                        objective = structure.get("objective", objective)
                        constraints = structure.get("constraints", constraints)
                        depth_level = structure.get("depth_level", depth_level)
                        reasoning_style = structure.get("reasoning_style", reasoning_style)
                except:
                    pass

            return PromptSynthesis(
                final_prompt=final_text,
                prompt_structure=PromptStructure(
                    context=context,
                    objective=objective,
                    constraints=constraints,
                    depth_level=depth_level,
                    reasoning_style=reasoning_style
                ),
                optimization_notes=["Converted raw thought via Senior Architect Engine"],
                confidence=0.95
            )

        except Exception as e:
            logger.error(f"REAL LLM Synthesis failed: {str(e)}")
            # STOP THE FAKE FALLBACK - Tell the user the truth!
            error_msg = f"BRAIN ERROR: {str(e)}. Check your API key in .env!"
            return PromptSynthesis(
                final_prompt=error_msg,
                prompt_structure=PromptStructure(
                    context="Error State", objective="Error Reporting", constraints=[], depth_level="N/A", reasoning_style="N/A"
                ),
                optimization_notes=[f"Failed with error: {str(e)}"],
                confidence=0.0
            )
