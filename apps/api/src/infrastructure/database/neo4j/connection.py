import os
from neo4j import AsyncGraphDatabase
from src.config.settings import get_settings

settings = get_settings()

class Neo4jManager:
    def __init__(self):
        self._uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self._user = os.getenv("NEO4J_USER", "neo4j")
        self._password = os.getenv("NEO4J_PASSWORD", "password")
        self._driver = None

    async def connect(self):
        if not self._driver:
            self._driver = AsyncGraphDatabase.driver(self._uri, auth=(self._user, self._password))

    async def close(self):
        if self._driver:
            await self._driver.close()
            self._driver = None

    async def get_session(self):
        if not self._driver:
            await self.connect()
        return self._driver.session()

neo4j_manager = Neo4jManager()
