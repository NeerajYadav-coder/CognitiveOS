from src.orchestration.pipeline_manager import CognitivePipeline
from src.pipelines.engines import (
    IntentEngine,
    ModeDetectorEngine,
    AmbiguityEngine,
    VocabularyEngine,
    ThoughtStructurerEngine,
    PromptSynthesizerEngine,
    MemoryProfileEngine,
    ReflectionEngine,
    SemanticGraphEngine,
    MultiAgentCollaborationEngine,
    AutonomousResearchEngine,
    IntegrationEngine,
    CognitiveOSEngine,
    GovernanceEngine,
    EvolutionEngine
)

def build_core_cognitive_pipeline() -> CognitivePipeline:
    """
    Assembles the core cognitive pipeline.
    Engines are executed sequentially in the exact order defined here.
    Data is passed seamlessly via the CognitiveState object.
    """
    return CognitivePipeline(
        name="CoreCognitivePipeline",
        engines=[
            IntentEngine(),
            ModeDetectorEngine(),
            AmbiguityEngine(),
            VocabularyEngine(),
            ThoughtStructurerEngine(),
            AutonomousResearchEngine(),
            MultiAgentCollaborationEngine(),
            IntegrationEngine(),
            PromptSynthesizerEngine(),
            MemoryProfileEngine(),
            ReflectionEngine(),
            SemanticGraphEngine(),
            CognitiveOSEngine(),
            GovernanceEngine(),
            EvolutionEngine()
        ]
    )

# Singleton instance for the application
core_pipeline = build_core_cognitive_pipeline()
