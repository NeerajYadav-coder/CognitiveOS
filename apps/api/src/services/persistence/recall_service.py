import uuid
from typing import List, Dict, Any
from src.infrastructure.repositories.vector import VectorMemoryRepository
from src.infrastructure.repositories.graph import SemanticGraphRepository

class SemanticRecallService:
    """
    Orchestrates the retrieval of contextually relevant information from 
    both vector memory and the knowledge graph.
    """
    def __init__(self, vector_repo: VectorMemoryRepository, graph_repo: SemanticGraphRepository):
        self.vector_repo = vector_repo
        self.graph_repo = graph_repo

    async def recall_context(self, user_id: uuid.UUID, query_embedding: List[float], concepts: List[str]) -> Dict[str, Any]:
        """
        Performs hybrid recall: 
        1. Semantic similarity from vector DB
        2. Relationship discovery from Graph DB
        """
        # Vector Similarity
        memories = await self.vector_repo.semantic_search(user_id, query_embedding)
        
        # Graph Context
        graph_context = []
        for concept in concepts:
            neighbors = await self.graph_repo.get_neighborhood(concept, depth=1)
            graph_context.extend(neighbors)
            
        return {
            "episodic_memories": [m.raw_content for m in memories],
            "graph_context": graph_context
        }
