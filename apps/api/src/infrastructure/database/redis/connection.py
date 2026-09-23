import redis.asyncio as redis
from src.config.settings import get_settings

settings = get_settings()

class RedisManager:
    def __init__(self):
        self._redis_url = settings.REDIS_URL
        self._client: Optional[redis.Redis] = None

    async def connect(self):
        if not self._client:
            self._client = redis.from_url(self._redis_url, decode_responses=True)

    async def close(self):
        if self._client:
            await self._client.close()
            self._client = None

    @property
    def client(self) -> redis.Redis:
        if not self._client:
            raise RuntimeError("Redis not connected. Call connect() first.")
        return self._client

redis_manager = RedisManager()
