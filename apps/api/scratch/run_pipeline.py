import asyncio
import sys
import os

# Add the src directory to the path so we can import modules correctly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock FastAPI for execution in environments without it
from unittest.mock import MagicMock
mock_fastapi = MagicMock()
sys.modules["fastapi"] = mock_fastapi
sys.modules["fastapi.responses"] = MagicMock()
mock_fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR = 500
mock_fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY = 422

from src.schemas.cognitive import CognitiveState
from src.pipelines.main_pipeline import build_core_cognitive_pipeline

async def run_demo():
    pipeline = build_core_cognitive_pipeline()
    
    # Sample input representing a complex, slightly ambiguous, and deep intellectual inquiry
    raw_input = "I feel disconnected from the modern architectural landscape, everything feels shallow and optimized for efficiency but devoid of biological or philosophical meaning. How can we build systems that scale like software but breathe like living organisms?"
    
    state = CognitiveState(
        session_id="demo-session-001",
        raw_input=raw_input
    )
    
    print(f"--- STARTING COGNITIVE PIPELINE ---\n")
    print(f"Input: {raw_input}\n")
    
    processed_state = await pipeline.run(state)
    
    print(f"\n--- PIPELINE EXECUTION COMPLETE ---\n")
    
    print(f"1. Intent Domain: {processed_state.intent.domain if processed_state.intent else 'N/A'}")
    print(f"2. Cognitive Modes: {[m.name for m in processed_state.mode.modes] if processed_state.mode else 'N/A'}")
    print(f"3. Ambiguity Score: {processed_state.ambiguity.ambiguity_score if processed_state.ambiguity else 'N/A'}")
    print(f"4. Vocabulary Suggestions: {len(processed_state.vocabulary.recommended_terms) if processed_state.vocabulary else 'N/A'}")
    print(f"5. Thought Structure Type: {processed_state.thought_structure.structured_thought.thinking_structure if processed_state.thought_structure else 'N/A'}")
    print(f"6. Collaboration Insight Synthesis: {processed_state.collaboration.synthesized_insight[:100]}..." if processed_state.collaboration else "N/A")
    print(f"7. Research Modes: {processed_state.research.research_mode if processed_state.research else 'N/A'}")
    print(f"8. Semantic Graph Nodes: {len(processed_state.semantic_graph.concept_nodes) if processed_state.semantic_graph else 'N/A'}")
    print(f"9. OS Environment Status: {processed_state.cos.environment_state.environment_status if processed_state.cos else 'N/A'}")
    print(f"10. Governance Compliance: {processed_state.governance.compliance_status if processed_state.governance else 'N/A'}")
    print(f"11. Evolution Recommendations: {len(processed_state.evolution.recommendations) if processed_state.evolution else 'N/A'}")
    
    print(f"\nFinal Prompt Synthesis Snippet:\n{processed_state.synthesis.final_prompt[:300]}...\n" if processed_state.synthesis else "\nPrompt Synthesis: N/A\n")

if __name__ == "__main__":
    asyncio.run(run_demo())
