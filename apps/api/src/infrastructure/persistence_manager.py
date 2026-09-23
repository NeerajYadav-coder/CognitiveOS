import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.repositories.sqlalchemy import SQLAlchemyRepository
from src.infrastructure.repositories.vector import VectorMemoryRepository
from src.infrastructure.repositories.graph import SemanticGraphRepository
from src.infrastructure.database.postgres.models import CognitiveInteraction, PromptOutput

class CognitivePersistenceManager:
    """
    The Orchestrator for all persistence activities.
    Coordinates Postgres (structured), pgvector (semantic), and Neo4j (graph).
    """
    def __init__(self, session: AsyncSession):
        self.session = session
        self.interaction_repo = SQLAlchemyRepository(session, CognitiveInteraction)
        self.prompt_repo = SQLAlchemyRepository(session, PromptOutput)
        self.vector_repo = VectorMemoryRepository(session)
        self.graph_repo = SemanticGraphRepository()

    async def persist_cognitive_event(self, state_dict: dict, user_id: uuid.UUID, session_id: uuid.UUID):
        """
        Decomposes a CognitiveState into structured, semantic, and graph components.
        """
        # Pack full cognitive telemetry into Postgres orchestration_trace JSONB
        trace_data = state_dict.get("metadata", {}) or {}
        trace_data["semantic_graph"] = state_dict.get("semantic_graph", {})
        trace_data["vocabulary"] = state_dict.get("vocabulary", {})
        trace_data["synthesis"] = state_dict.get("synthesis", {})
        trace_data["thought_structure"] = state_dict.get("thought_structure", {})

        # 1. Persist Structured Interaction (Postgres)
        interaction = CognitiveInteraction(
            session_id=session_id,
            raw_input=state_dict["raw_input"],
            intent_output=state_dict.get("intent", {}),
            cognitive_mode=state_dict.get("mode", {}),
            ambiguity_score=state_dict.get("ambiguity", {}).get("ambiguity_score", 0.0),
            orchestration_trace=trace_data
        )
        await self.interaction_repo.create(interaction)

        # 2. Persist Semantic Memory (pgvector)
        # Assuming embedding service is called elsewhere or here
        # self.vector_repo.create(...)

        # 3. Persist Graph Relationships (Neo4j)
        graph_data = state_dict.get("semantic_graph", {})
        try:
            for node in graph_data.get("concept_nodes", []):
                await self.graph_repo.create_concept(node["label"], node["domain"], node.get("attributes", {}))
            
            for rel in graph_data.get("semantic_relationships", []):
                await self.graph_repo.create_relationship(rel["source"], rel["target"], rel["relationship_type"], rel["confidence"])
        except Exception as graph_err:
            import logging
            logging.getLogger("cognitiveos.api").warning(f"Neo4j graph storage offline: {str(graph_err)}")

        await self.session.commit()
        return interaction.id
