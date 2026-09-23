import asyncio
import os
import sys

# Add apps/api to path so imports work correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.synthesis.engine import SynthesisLLMService
from src.schemas.cognitive import UserContext, DomainExpertise, IntentExtraction, CognitiveMode, AmbiguityAnalysis, VocabularyExpansion, ThoughtStructure, StructuredThought

async def run_test():
    raw_prompt = (
        "Hey, as you know, as I told you that I have decided to live in a solitude life, "
        "it's not a new thing for me because earlier, one and a half year, I was in my solitude phase "
        "and I did incredible things, creation, observing things, and having experienced those, "
        "I can never have with the peoples around me. So, it's amazing. Now, I'm going to ask that, "
        "as you know, I'm a curious person, I really wanna understand the nature of the universe and all. "
        "What are the things, techniques, whatever, like, you know that, try to understand what I'm saying. "
        "So in my solitude phase, I really want to experience those stuff. For example, meditation is one of "
        "the things that I really wanna experience in the, like, very deeply, like, what is it? "
        "Like, you know, by, by doing, by experiencing. And what are the techniques that exist? "
        "What are the, not just techniques, but whatever, whatever that, that I must, I must experience, "
        "or I should experience if I'm in my solitude phase. So, I really wanna, so tell me incredible things "
        "in, in all the human, uh, human history, human existence. Uh, yeah, please. Whatever incredible stuff, "
        "like, you know, very powerful, uh, kind of things that, you know, human discovered, and they are kind "
        "of very underrated or maybe they are, the people don't know much about them. And they can really "
        "change my, whatever, like, mindset, the way I'm experiencing the world, the way I'm observing the nature, "
        "myself and all. You know, try to understand what I'm, try to understand my intention."
    )

    # Common upstream inputs for both tests (mocked from typical analyzer output)
    intent = IntentExtraction(primary_intent="Exploration / Inquiry", confidence=0.95, domain="Philosophy / Psychology")
    mode = CognitiveMode(modes=[{"name": "exploratory", "confidence": 0.9}, {"name": "philosophical", "confidence": 0.85}])
    ambiguity = AmbiguityAnalysis(ambiguity_score=0.2)
    vocabulary = VocabularyExpansion(
        core_expression="solitude and meditation",
        semantic_expansions=[],
        adjacent_concepts=["existential exploration", "phenomenology", "state space of consciousness"],
        recommended_terms=["phenomenology", "consciousness expansion", "solitary introspection"]
    )
    thought = ThoughtStructure(
        structured_thought=StructuredThought(
            core_question="What deep human discoveries, meditative techniques, and experiences should one explore during a phase of solitude to expand consciousness?",
            exploration_direction="Exploring underrated practices, cognitive transformations, and historical paradigms of solitude.",
            subtopics=["Meditation mechanics", "Phenomenological shifts", "Underrated historical practices"],
            missing_context=[],
            possible_domains=["Philosophy", "Cognitive Science"],
            thinking_structure="exploratory"
        )
    )

    service = SynthesisLLMService()

    # 1. Test case: Philosopher Builder
    philosopher_context = UserContext(
        user_id="00000000-0000-0000-0000-000000000001",
        profession="philosopher builder",
        intellectual_level="expert",
        cognitive_style={
            "verbosity": "detailed",
            "reasoning_preference": "analogy-driven"
        },
        domain_expertise=[
            DomainExpertise(domain="Philosophy of Mind", level="expert"),
            DomainExpertise(domain="Ontology", level="expert")
        ]
    )

    print("\n--- RUNNING SYNTHESIS FOR: philosopher builder ---")
    synthesis_philosopher = await service.synthesize_prompt(
        raw_input=raw_prompt,
        intent=intent,
        mode=mode,
        ambiguity=ambiguity,
        vocabulary=vocabulary,
        thought=thought,
        user_context=philosopher_context
    )

    # 2. Test case: Software Engineer
    engineer_context = UserContext(
        user_id="00000000-0000-0000-0000-000000000001",
        profession="software engineer",
        intellectual_level="expert",
        cognitive_style={
            "verbosity": "detailed",
            "reasoning_preference": "first-principles"
        },
        domain_expertise=[
            DomainExpertise(domain="Systems Architecture", level="expert"),
            DomainExpertise(domain="Distributed Systems", level="expert")
        ]
    )

    print("\n--- RUNNING SYNTHESIS FOR: software engineer ---")
    synthesis_engineer = await service.synthesize_prompt(
        raw_input=raw_prompt,
        intent=intent,
        mode=mode,
        ambiguity=ambiguity,
        vocabulary=vocabulary,
        thought=thought,
        user_context=engineer_context
    )

    # Save outputs to file so we can view them
    result_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_synthesis_results.txt")
    with open(result_path, "w") as f:
        f.write("=== PHILOSOPHER BUILDER SYNTHESIS ===\n")
        f.write(synthesis_philosopher.final_prompt)
        f.write("\n\n")
        f.write("=== SOFTWARE ENGINEER SYNTHESIS ===\n")
        f.write(synthesis_engineer.final_prompt)
        f.write("\n")

    print(f"\n✅ Results successfully written to: {result_path}")

if __name__ == "__main__":
    asyncio.run(run_test())
