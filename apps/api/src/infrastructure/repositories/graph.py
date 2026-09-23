from typing import List, Dict, Any
from src.infrastructure.database.neo4j.connection import neo4j_manager

class SemanticGraphRepository:
    """
    Handles graph-based cognition storage and traversal in Neo4j.
    """
    async def create_concept(self, label: str, domain: str, attributes: Dict[str, Any]):
        async with await neo4j_manager.get_session() as session:
            query = (
                "MERGE (c:Concept {label: $label}) "
                "SET c.domain = $domain, c.attributes = $attributes "
                "RETURN c"
            )
            await session.run(query, label=label, domain=domain, attributes=attributes)

    async def create_relationship(self, source_label: str, target_label: str, rel_type: str, weight: float):
        async with await neo4j_manager.get_session() as session:
            query = (
                "MATCH (a:Concept {label: $source}), (b:Concept {label: $target}) "
                f"MERGE (a)-[r:{rel_type}]->(b) "
                "SET r.weight = $weight "
                "RETURN r"
            )
            await session.run(query, source=source_label, target=target_label, weight=weight)

    async def get_neighborhood(self, label: str, depth: int = 1) -> List[Dict[str, Any]]:
        async with await neo4j_manager.get_session() as session:
            query = (
                "MATCH (c:Concept {label: $label})-[r*..$depth]-(neighbor) "
                "RETURN c, r, neighbor"
            )
            result = await session.run(query, label=label, depth=depth)
            return [record.data() for record in await result.list()]
