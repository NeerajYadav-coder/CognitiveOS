import re
import json
from typing import List, Tuple, Optional
from openai import AsyncOpenAI

from src.config.settings import get_settings
from src.schemas.cognitive import SpokenThoughtAnalysis
from src.utils.logger import logger

settings = get_settings()

COMMON_FILLERS = [
    r"\bum+\b",
    r"\buh+\b",
    r"\byou know\b",
    r"\bi mean\b",
    r"\bsort of\b",
    r"\bkind of\b",
    r"\bbasically\b",
    r"\bliterally\b",
    r"\bactually\b",
    r"\bso yeah\b",
    r"\banyway\b",
    r"\bright\b(?=,|$)",
]

VAGUE_INDICATORS = [
    "stuff", "things", "something", "somewhere", "somehow", 
    "maybe", "probably", "not sure", "dunno", "whatever"
]

def clean_verbal_fillers(raw_text: str) -> Tuple[str, List[str]]:
    """Strips common spoken disfluencies and verbal filler words."""
    cleaned = raw_text
    found_fillers = []

    for pattern in COMMON_FILLERS:
        matches = re.findall(pattern, cleaned, flags=re.IGNORECASE)
        if matches:
            found_fillers.extend([m.lower() for m in matches])
            cleaned = re.sub(pattern, " ", cleaned, flags=re.IGNORECASE)

    # Remove stuttered duplicate words (e.g., "the the", "I I")
    duplicate_pattern = r"\b(\w+)\s+\1\b"
    while re.search(duplicate_pattern, cleaned, flags=re.IGNORECASE):
        cleaned = re.sub(duplicate_pattern, r"\1", cleaned, flags=re.IGNORECASE)

    # Clean redundant whitespace and punctuation
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    cleaned = re.sub(r"\s+([,.?!])", r"\1", cleaned)
    
    if cleaned and cleaned[0].islower():
        cleaned = cleaned[0].upper() + cleaned[1:]

    return cleaned, list(set(found_fillers))

def calculate_spoken_ambiguity(raw_text: str, cleaned_text: str, filler_count: int) -> float:
    """Calculates ambiguity rating of spoken discourse based on fillers and vague words."""
    words = raw_text.split()
    total_words = max(len(words), 1)
    
    filler_ratio = min(filler_count / total_words, 0.4) * 2.0  # 0 to 0.8
    
    vague_matches = sum(1 for v in VAGUE_INDICATORS if re.search(rf"\b{v}\b", raw_text, re.IGNORECASE))
    vague_penalty = min(vague_matches * 0.1, 0.4)
    
    length_penalty = 0.2 if total_words < 8 else 0.0
    
    score = min(max(0.15 + (filler_ratio * 0.5) + vague_penalty + length_penalty, 0.05), 0.95)
    return round(score, 2)


class SpokenThoughtEngine:
    """
    Ingests raw speech transcriptions, strips verbal noise,
    extracts latent hypotheses, and structures stream-of-consciousness into actionable prompts.
    """

    def __init__(self, client: Optional[AsyncOpenAI] = None):
        self._client = client or AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_API_BASE
        )

    async def process(self, raw_speech: str) -> SpokenThoughtAnalysis:
        cleaned_text, fillers = clean_verbal_fillers(raw_speech)
        ambiguity_score = calculate_spoken_ambiguity(raw_speech, cleaned_text, len(fillers))

        # Try LLM for rich cognitive analysis
        try:
            prompt_system = (
                "You are the CognitiveOS Spoken Thought Synthesizer. "
                "The user is speaking aloud into a microphone. "
                "Extract the core implicit intent, identify 1-3 latent hypotheses, "
                "formulate a single crisp focal question, and synthesize a high-signal LLM prompt. "
                "Respond ONLY with a valid JSON object matching the requested schema."
            )
            prompt_user = (
                f"Spoken raw transcript: \"{raw_speech}\"\n"
                f"Cleaned transcript: \"{cleaned_text}\"\n\n"
                "Return JSON with keys: implicit_intent, latent_hypotheses (list), focal_question, suggested_prompt."
            )

            response = await self._client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": prompt_system},
                    {"role": "user", "content": prompt_user}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            raw_json = response.choices[0].message.content.strip()
            raw_json = raw_json.replace("```json", "").replace("```", "").strip()
            data = json.loads(raw_json)

            return SpokenThoughtAnalysis(
                cleaned_transcript=cleaned_text,
                filler_words_removed=fillers,
                implicit_intent=data.get("implicit_intent", "Explore ideas from spoken input"),
                latent_hypotheses=data.get("latent_hypotheses", []),
                spoken_ambiguity_score=ambiguity_score,
                focal_question=data.get("focal_question", "What is the primary outcome you want to achieve?"),
                suggested_prompt=data.get("suggested_prompt", cleaned_text)
            )

        except Exception as e:
            logger.warning(f"LLM SpokenThoughtEngine failed or unconfigured: {str(e)}. Using heuristic synthesis.")
            return self._heuristic_fallback(raw_speech, cleaned_text, fillers, ambiguity_score)

    def _heuristic_fallback(
        self, raw_speech: str, cleaned_text: str, fillers: List[str], ambiguity_score: float
    ) -> SpokenThoughtAnalysis:
        # Heuristic intent formulation
        lead_words = cleaned_text.split()[:12]
        intent_summary = " ".join(lead_words)
        if len(cleaned_text.split()) > 12:
            intent_summary += "..."

        hypotheses = []
        if "connect" in cleaned_text.lower() or "between" in cleaned_text.lower():
            hypotheses.append("Explores structural analogies across multiple domains")
        if "build" in cleaned_text.lower() or "make" in cleaned_text.lower() or "create" in cleaned_text.lower():
            hypotheses.append("Aims for a concrete implementation or architectural prototype")
        if not hypotheses:
            hypotheses.append("Seeks conceptual clarity and systematic framework decomposition")

        focal_question = f"How should we best structure the exploration of '{cleaned_text[:50]}...'?"
        suggested_prompt = (
            f"Analyze and systematically expand upon this core concept:\n\n"
            f"> {cleaned_text}\n\n"
            f"Provide a structured decomposition covering: 1) First Principles, 2) Key Trade-offs, and 3) Actionable Next Steps."
        )

        return SpokenThoughtAnalysis(
            cleaned_transcript=cleaned_text,
            filler_words_removed=fillers,
            implicit_intent=f"Investigate: {intent_summary}",
            latent_hypotheses=hypotheses,
            spoken_ambiguity_score=ambiguity_score,
            focal_question=focal_question,
            suggested_prompt=suggested_prompt
        )
