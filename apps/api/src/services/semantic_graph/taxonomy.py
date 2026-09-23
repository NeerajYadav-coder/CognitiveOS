from enum import Enum

class RelationshipType(str, Enum):
    SEMANTIC_SIMILARITY = "semantic_similarity"
    PHILOSOPHICAL_ASSOCIATION = "philosophical_association"
    CAUSAL_RELATIONSHIP = "causal_relationship"
    HIERARCHICAL_RELATIONSHIP = "hierarchical_relationship"
    CONCEPTUAL_DEPENDENCY = "conceptual_dependency"
    HISTORICAL_CONNECTION = "historical_connection"
    CROSS_DOMAIN_ANALOGY = "cross_domain_analogy"
    COMPLEMENTARY_CONCEPT = "complementary_concept"
    CONTRADICTORY_CONCEPT = "contradictory_concept"
    EMERGENT_RELATIONSHIP = "emergent_relationship"
