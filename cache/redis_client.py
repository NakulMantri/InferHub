import json
import redis.asyncio as redis
from core.config import settings
from core.logger import logger

class RedisCache:
    def __init__(self):
        self.redis: redis.Redis | None = None

    async def connect(self):
        try:
            self.redis = redis.from_url(settings.redis_url, decode_responses=True)
            await self.redis.ping()
            logger.info("Connected to Redis successfully.")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis = None

    async def disconnect(self):
        if self.redis:
            await self.redis.close()

    async def get_cached_response(self, model: str, prompt: str) -> str | None:
        if not self.redis:
            return None
        
        key = f"cache:{model}:{prompt}"
        try:
            val = await self.redis.get(key)
            return val
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None

    async def set_cached_response(self, model: str, prompt: str, response: str, ttl: int = 3600):
        if not self.redis:
            return
        
        key = f"cache:{model}:{prompt}"
        try:
            await self.redis.setex(key, ttl, response)
        except Exception as e:
            logger.error(f"Redis set error: {e}")

redis_client = RedisCache()
