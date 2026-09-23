import pytest
import uuid
from src.infrastructure.repositories.vector import VectorMemoryRepository
from src.infrastructure.database.vector.models import SemanticMemory
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio
async def test_vector_similarity_search(db_session: AsyncSession):
    repo = VectorMemoryRepository(db_session)
    user_id = uuid.uuid4()
    
    # Create mock memory
    memory = SemanticMemory(
        id=uuid.uuid4(),
        user_id=user_id,
        content_type="test",
        content_id=uuid.uuid4(),
        raw_content="CognitiveOS is an operating layer for AI.",
        embedding=[0.1] * 1536,
        metadata_fields={}
    )
    db_session.add(memory)
    await db_session.commit()
    
    # Search with exact embedding
    results = await repo.semantic_search(user_id, [0.1] * 1536, limit=1)
    
    assert len(results) == 1
    assert results[0].raw_content == "CognitiveOS is an operating layer for AI."

@pytest.mark.asyncio
async def test_graph_traversal(neo4j_session):
    from src.infrastructure.repositories.graph import SemanticGraphRepository
    repo = SemanticGraphRepository()
    
    await repo.create_concept("Cognition", "Neuroscience", {})
    await repo.create_concept("AI", "Computer Science", {})
    await repo.create_relationship("Cognition", "AI", "RELATED_TO", 0.9)
    
    neighborhood = await repo.get_neighborhood("Cognition")
    assert len(neighborhood) > 0
    assert any(n['neighbor']['label'] == 'AI' for n in neighborhood)
