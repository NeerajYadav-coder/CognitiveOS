import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.config.settings import get_settings
from src.infrastructure.database.neo4j.connection import neo4j_manager

settings = get_settings()

@pytest_asyncio.fixture
async def db_session():
    # Create engine and session factory
    engine = create_async_engine(settings.DATABASE_URL)
    async_session_factory = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session_factory() as session:
        yield session
        # Rollback changes to keep tests isolated
        await session.rollback()
        
    await engine.dispose()

@pytest.fixture
def mock_neo4j():
    # Mock neo4j_manager session logic
    mock_session = AsyncMock()
    
    concepts = {}
    relationships = []
    
    async def mock_run(query, **kwargs):
        # MERGE (c:Concept {label: $label})
        if "MERGE (c:Concept" in query:
            label = kwargs["label"]
            domain = kwargs.get("domain")
            attrs = kwargs.get("attributes", {})
            concepts[label] = {"label": label, "domain": domain, "attributes": attrs}
        # MATCH (a:Concept {label: $source}), (b:Concept {label: $target}) MERGE (a)-[r:...]
        elif "MERGE (a)-[r:" in query:
            source = kwargs["source"]
            target = kwargs["target"]
            weight = kwargs.get("weight", 1.0)
            relationships.append({"source": source, "target": target, "weight": weight})
        # MATCH (c:Concept {label: $label})-[r*..$depth]-(neighbor)
        elif "MATCH (c:Concept" in query:
            label = kwargs["label"]
            neighbors = []
            for r in relationships:
                if r["source"] == label:
                    neighbors.append({
                        "neighbor": concepts.get(r["target"], {"label": r["target"]}),
                        "relationship": {"weight": r["weight"]}
                    })
                elif r["target"] == label:
                    neighbors.append({
                        "neighbor": concepts.get(r["source"], {"label": r["source"]}),
                        "relationship": {"weight": r["weight"]}
                    })
            
            class MockRecord:
                def __init__(self, data_dict):
                    self._data = data_dict
                def data(self):
                    return self._data

            records = [MockRecord(n) for n in neighbors]
            mock_result = AsyncMock()
            mock_result.list = AsyncMock(return_value=records)
            return mock_result
        return AsyncMock()

    mock_session.run = mock_run
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)
    
    original_get_session = neo4j_manager.get_session
    neo4j_manager.get_session = AsyncMock(return_value=mock_session)
    
    yield mock_session
    
    neo4j_manager.get_session = original_get_session

@pytest.fixture
def neo4j_session(mock_neo4j):
    return mock_neo4j
