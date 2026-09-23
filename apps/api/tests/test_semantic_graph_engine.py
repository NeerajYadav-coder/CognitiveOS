import pytest
import asyncio
from src.schemas.cognitive import SemanticGraph, SemanticNode, SemanticRelationship, ExplorationPath
from src.services.semantic_graph.heuristics import prevent_rigid_ontology, validate_cross_domain_exploration
from src.services.semantic_graph.engine import SemanticGraphLLMService

def test_prevent_rigid_ontology():
    # Setup graph with an absolute truth confidence
    graph = SemanticGraph(
        concept_nodes=[],
        semantic_relationships=[
            SemanticRelationship(source="a", target="b", relationship_type="causal", confidence=1.0, explanation="A causes B")
        ],
        adjacent_domains=[], exploration_paths=[], semantic_clusters=[], confidence=0.9
    )
    
    result = prevent_rigid_ontology(graph)
    
    # Assert confidence was softened
    assert result.semantic_relationships[0].confidence == 0.95

def test_validate_cross_domain_exploration():
    graph = SemanticGraph(
        concept_nodes=[],
        semantic_relationships=[],
        adjacent_domains=["Neuroscience"], 
        exploration_paths=[
            ExplorationPath(path_name="Algorithms", nodes=["x", "y"], rationale="Exploring sorting logic.")
        ], 
        semantic_clusters=[], confidence=0.8
    )
    
    result = validate_cross_domain_exploration(graph)
    
    # Assert prompt to bridge domains was injected
    assert "Encourages bridging with Neuroscience" in result.exploration_paths[0].rationale

@pytest.mark.asyncio
async def test_semantic_graph_llm_service():
    service = SemanticGraphLLMService()
    
    result = await service.build_graph(
        raw_input="I am designing a scalable system architecture.",
        thought=None, vocabulary=None, reflection=None
    )
    
    assert result.concept_nodes is not None
    assert len(result.concept_nodes) > 0
    assert any("Computer Science" in n.domain for n in result.concept_nodes)
    assert len(result.exploration_paths) > 0
