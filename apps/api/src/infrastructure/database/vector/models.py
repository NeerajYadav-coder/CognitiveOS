from __future__ import annotations
from typing import List, Optional
import uuid

from sqlalchemy import Column, String, ForeignKey, Table, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from pgvector.sqlalchemy import Vector as PGVector

import numpy as np

class Vector(PGVector):
    cache_ok = True
    def bind_processor(self, dialect):
        return lambda value: value

    def result_processor(self, dialect, coltype):
        def process(value):
            if value is None:
                return value
            if isinstance(value, (list, np.ndarray)):
                return value
            if isinstance(value, str):
                return np.array(value[1:-1].split(','), dtype=np.float32)
            return value
        return process
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.postgres.models import Base

class SemanticMemory(Base):
    __tablename__ = "semantic_memories"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    content_type: Mapped[str] = mapped_column(String(50), index=True) # e.g. 'prompt', 'reflection', 'research'
    content_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True)) # ID in the primary table
    raw_content: Mapped[str] = mapped_column(Text)
    
    # 1536 is standard for OpenAI gpt-4o / text-embedding-3-small
    embedding: Mapped[Vector] = mapped_column(Vector())
    
    metadata_fields: Mapped[dict] = mapped_column(JSONB, default={})
