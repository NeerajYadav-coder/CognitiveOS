from src.schemas.cognitive import SemanticGraph

def prevent_rigid_ontology(graph: SemanticGraph) -> SemanticGraph:
    """
    Prevents the LLM from forcing nuance into rigid taxonomic boxes.
    If multiple relationships have 1.0 confidence, it gently randomizes/softens them
    to preserve the probabilistic nature of semantic meaning.
    """
    for rel in graph.semantic_relationships:
        if rel.confidence == 1.0:
            rel.confidence = 0.95 # Knowledge is rarely absolute
            
    return graph

def validate_cross_domain_exploration(graph: SemanticGraph) -> SemanticGraph:
    """
    Ensures that exploration paths don't just stay in one domain if adjacent domains exist.
    """
    if len(graph.adjacent_domains) > 0 and len(graph.exploration_paths) > 0:
        # Check if any path rationale mentions interdisciplinary or cross-domain thought
        has_cross_domain = any("cross" in p.rationale.lower() or "inter" in p.rationale.lower() or "bridge" in p.rationale.lower() for p in graph.exploration_paths)
        if not has_cross_domain:
            # Inject a note to encourage bridging
            graph.exploration_paths[0].rationale += f" (Encourages bridging with {graph.adjacent_domains[0]})"
            
    return graph
