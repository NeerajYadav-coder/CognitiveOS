import json
import uuid
from typing import Optional, Any
from src.infrastructure.database.redis.connection import redis_manager

class RedisContextManager:
    """
    Manages real-time cognitive state and distributed locks in Redis.
    """
    def __init__(self):
        self.client = redis_manager.client

    async def save_active_context(self, session_id: uuid.UUID, state: dict, ttl: int = 3600):
        await self.client.setex(
            f"context:{session_id}",
            ttl,
            json.dumps(state)
        )

    async def get_active_context(self, session_id: uuid.UUID) -> Optional[dict]:
        data = await self.client.get(f"context:{session_id}")
        return json.loads(data) if data else None

    async def acquire_lock(self, lock_name: str, timeout: int = 10) -> bool:
        return await self.client.set(
            f"lock:{lock_name}",
            "locked",
            ex=timeout,
            nx=True
        )

    async def release_lock(self, lock_name: str):
        await self.client.delete(f"lock:{lock_name}")
