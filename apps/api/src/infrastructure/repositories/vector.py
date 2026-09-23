from typing import List, Optional
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from src.infrastructure.database.vector.models import SemanticMemory
from src.infrastructure.repositories.sqlalchemy import SQLAlchemyRepository

class VectorMemoryRepository(SQLAlchemyRepository[SemanticMemory]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, SemanticMemory)

    async def semantic_search(self, user_id: uuid.UUID, embedding: List[float], limit: int = 5) -> List[SemanticMemory]:
        """
        Performs vector similarity search using L2 distance (or cosine distance).
        pgvector provides the <-> (L2), <#> (negative inner product), and <=> (cosine distance) operators.
        Falls back to in-memory cosine similarity if pgvector is not available in the database.
        """
        try:
            # Try native pgvector query
            stmt = (
                select(SemanticMemory)
                .where(SemanticMemory.user_id == user_id)
                .order_by(SemanticMemory.embedding.cosine_distance(embedding))
                .limit(limit)
            )
            result = await self.session.execute(stmt)
            return result.scalars().all()
        except Exception:
            # Rollback current transaction state in session so we can run queries again
            await self.session.rollback()
            
            # Fallback to in-memory cosine similarity
            stmt = (
                select(SemanticMemory)
                .where(SemanticMemory.user_id == user_id)
            )
            result = await self.session.execute(stmt)
            memories = result.scalars().all()
            
            # Compute cosine similarity in Python using NumPy
            import numpy as np
            
            target = np.array(embedding)
            target_norm = np.linalg.norm(target)
            
            def get_similarity(mem):
                if not mem.embedding:
                    return -1.0
                mem_emb = np.array(mem.embedding)
                mem_norm = np.linalg.norm(mem_emb)
                if target_norm == 0.0 or mem_norm == 0.0:
                    return 0.0
                return np.dot(target, mem_emb) / (target_norm * mem_norm)
            
            # Sort descending by similarity
            memories.sort(key=get_similarity, reverse=True)
            return memories[:limit]
