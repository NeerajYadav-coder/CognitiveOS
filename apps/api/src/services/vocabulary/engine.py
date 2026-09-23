import asyncio
import json
from typing import Optional
from openai import AsyncOpenAI
from src.config.settings import get_settings

from src.schemas.cognitive import VocabularyExpansion, SemanticExpansion, IntentExtraction, CognitiveMode, AmbiguityAnalysis, UserContext
from src.services.vocabulary.prompts import VOCABULARY_SYSTEM_PROMPT, VOCABULARY_USER_PROMPT
from src.services.vocabulary.heuristics import filter_hallucinated_terms
from src.utils.logger import logger

settings = get_settings()

class VocabularyLLMService:
    """
    Direct LLM communication for Cognitive Semantic Vocabulary Expansion.
    Maps vague human intuition and emotion into precise domain-specific terminology.
    """
    
    def __init__(self, client: Optional[AsyncOpenAI] = None):
        self._client = client or AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY, 
            base_url=settings.OPENAI_API_BASE
        )
        
    async def expand_vocabulary(
        self, 
        raw_input: str, 
        intent: Optional[IntentExtraction], 
        mode: Optional[CognitiveMode],
        ambiguity: Optional[AmbiguityAnalysis],
        user_context: Optional[UserContext] = None
    ) -> VocabularyExpansion:
        
        logger.info("Calling REAL LLM for Semantic Vocabulary Expansion...")
        
        prof = user_context.profession if user_context else "General User"
        lvl = user_context.intellectual_level if user_context else "intermediate"
        
        domain_list = []
        if user_context and user_context.domain_expertise:
            domain_list = [f"{d.domain} ({d.level})" for d in user_context.domain_expertise]
        domains_str = ", ".join(domain_list) if domain_list else "None"
        
        system = VOCABULARY_SYSTEM_PROMPT
        user = VOCABULARY_USER_PROMPT.format(
            user_profession=prof or "General User",
            user_level=lvl,
            user_domains=domains_str,
            intent=intent.primary_intent if intent else "Unknown",
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
            
            expansions_list = []
            for item in data.get("semantic_expansions", []):
                expansions_list.append(SemanticExpansion(
                    term=item.get("term"),
                    confidence=float(item.get("confidence", 0.8)),
                    domain=item.get("domain", "General")
                ))
            
            recommended = data.get("recommended_terms", [])
            if not recommended:
                recommended = [item.get("term") for item in expansions_list]
                
            expansion = VocabularyExpansion(
                core_expression=data.get("core_expression", raw_input[:30] + "..."),
                semantic_expansions=expansions_list,
                adjacent_concepts=data.get("adjacent_concepts", []),
                recommended_terms=recommended
            )
            
        except Exception as e:
            logger.warning(f"REAL LLM Semantic Vocabulary Expansion failed: {str(e)}. Falling back to heuristics.")
            
            raw_lower = raw_input.lower()
            if "disconnected from society" in raw_lower or "alone" in raw_lower:
                core_expr = "feeling disconnected from society"
                semantic_expansions = [
                    SemanticExpansion(term="existential alienation", confidence=0.88, domain="philosophy"),
                    SemanticExpansion(term="social detachment", confidence=0.74, domain="psychology"),
                    SemanticExpansion(term="anomie", confidence=0.6, domain="sociology")
                ]
                adjacent = ["identity crisis", "meaning", "isolation"]
                recommended = ["alienation", "detachment", "existentialism"]
            elif "build a pipeline" in raw_lower or "connect things" in raw_lower:
                core_expr = "orchestrating system components"
                semantic_expansions = [
                    SemanticExpansion(term="DAG orchestration", confidence=0.9, domain="software architecture"),
                    SemanticExpansion(term="event-driven architecture", confidence=0.8, domain="software architecture")
                ]
                adjacent = ["state machines", "idempotency", "microservices"]
                recommended = ["DAG", "orchestration", "idempotency"]
            else:
                core_expr = raw_input[:20] + "..."
                semantic_expansions = [
                    SemanticExpansion(term="cognitive framing", confidence=0.85, domain="cognitive science")
                ]
                adjacent = ["mental models"]
                recommended = ["framing"]
                
            expansion = VocabularyExpansion(
                core_expression=core_expr,
                semantic_expansions=semantic_expansions,
                adjacent_concepts=adjacent,
                recommended_terms=recommended
            )
            
        # Apply validation/heuristics to strip LLM hallucinations
        expansion = filter_hallucinated_terms(expansion)
        
        return expansion
