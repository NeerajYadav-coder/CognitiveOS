from src.schemas.cognitive import VocabularyExpansion, SemanticExpansion

def filter_hallucinated_terms(expansion: VocabularyExpansion) -> VocabularyExpansion:
    """
    Prevents semantic distortion by stripping out recommended terms that have
    abnormally low confidence scores (< 0.5) from the semantic_expansions mapping.
    """
    valid_expansions = []
    valid_terms = []
    
    for exp in expansion.semantic_expansions:
        if exp.confidence >= 0.7:
            valid_expansions.append(exp)
            
    # Rebuild recommended terms based strictly on valid mappings
    valid_term_names = {e.term.lower() for e in valid_expansions}
    
    for term in expansion.recommended_terms:
        if term.lower() in valid_term_names or any(term.lower() in e.term.lower() for e in valid_expansions):
            valid_terms.append(term)
            
    expansion.semantic_expansions = valid_expansions
    expansion.recommended_terms = valid_terms if valid_terms else [e.term for e in valid_expansions]
    
    return expansion
