import asyncio
import json
from typing import Optional
from openai import AsyncOpenAI
from src.config.settings import get_settings

from src.schemas.cognitive import (
    ThoughtStructure, 
    StructuredThought, 
    IntentExtraction, 
    CognitiveMode, 
    AmbiguityAnalysis,
    VocabularyExpansion
)
from src.services.structuring.taxonomy import ThinkingStructureType
from src.services.structuring.heuristics import enforce_exploratory_preservation
from src.services.structuring.prompts import STRUCTURING_SYSTEM_PROMPT, STRUCTURING_USER_PROMPT
from src.utils.logger import logger

settings = get_settings()

class StructuringLLMService:
    """
    Direct LLM communication for the Thought Structuring Engine.
    Converts raw chaotic input into structured cognitive representation.
    """
    
    def __init__(self, client: Optional[AsyncOpenAI] = None):
        self._client = client or AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY, 
            base_url=settings.OPENAI_API_BASE
        )
        
    async def structure_thought(
        self, 
        raw_input: str, 
        intent: Optional[IntentExtraction], 
        mode: Optional[CognitiveMode],
        ambiguity: Optional[AmbiguityAnalysis],
        vocabulary: Optional[VocabularyExpansion]
    ) -> ThoughtStructure:
        
        logger.info("Calling REAL LLM for Thought Structuring...")
        
        system = STRUCTURING_SYSTEM_PROMPT
        user = STRUCTURING_USER_PROMPT.format(
            intent=intent.primary_intent if intent else "Unknown",
            modes=mode.primary_mode if mode else "Unknown",
            ambiguity=ambiguity.ambiguity_score if ambiguity else 0.5,
            vocabulary=", ".join(vocabulary.recommended_terms) if vocabulary else "None",
            raw_input=raw_input
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
            
            struct_data = data.get("structured_thought", {})
            if not struct_data or not isinstance(struct_data, dict):
                struct_data = data
                
            structured = StructuredThought(
                core_question=struct_data.get("core_question", "Unknown"),
                exploration_direction=struct_data.get("exploration_direction", "Unknown"),
                subtopics=struct_data.get("subtopics", []),
                missing_context=struct_data.get("missing_context", []),
                possible_domains=struct_data.get("possible_domains", []),
                thinking_structure=struct_data.get("thinking_structure", "exploratory")
            )
            
            thought_struct = ThoughtStructure(
                structured_thought=structured,
                clarified_representation=data.get("clarified_representation", raw_input),
                confidence=float(data.get("confidence", 0.9))
            )
            
        except Exception as e:
            logger.warning(f"REAL LLM Thought Structuring failed: {str(e)}. Falling back to heuristics.")
            
            raw_lower = raw_input.lower()
            if "disconnected" in raw_lower or "alone" in raw_lower:
                struct_type = ThinkingStructureType.PHILOSOPHICAL.value
                core = "What is the root cause and meaning behind the feeling of societal disconnection?"
                direction = "Philosophical and psychological exploration of identity and community."
                subtopics = ["Existential alienation", "Modern social structures", "Individual purpose"]
                clarified = "I am experiencing a profound sense of disconnection from society and want to explore the philosophical and psychological roots of this alienation."
            elif "bug" in raw_lower or "error" in raw_lower:
                struct_type = ThinkingStructureType.PROBLEM_SOLVING.value
                core = "Identify and resolve the root cause of the system error."
                direction = "Analytical debugging via component isolation."
                subtopics = ["Error logs", "Recent code changes", "Dependency conflicts"]
                clarified = "I need to systematically debug a software error by isolating components and analyzing logs."
            else:
                struct_type = ThinkingStructureType.EXPLORATORY.value
                core = "Wandering thought regarding abstract concepts."
                direction = "Open-ended conceptual mapping."
                subtopics = ["Concept A", "Concept B"]
                clarified = "I am curious about the relationship between these concepts and want to map them out."

            structured = StructuredThought(
                core_question=core,
                exploration_direction=direction,
                subtopics=subtopics,
                missing_context=["Specific timeframe", "External constraints"] if ambiguity and ambiguity.clarification_strategy.enabled else [],
                possible_domains=[vocabulary.semantic_expansions[0].domain] if vocabulary and vocabulary.semantic_expansions else ["General"],
                thinking_structure=struct_type
            )
            
            thought_struct = ThoughtStructure(
                structured_thought=structured,
                clarified_representation=clarified,
                confidence=0.89
            )
            
        # Apply Exploratory Protection Heuristic
        thought_struct = enforce_exploratory_preservation(thought_struct)
        
        return thought_struct
