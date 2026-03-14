import redis.asyncio as redis
from app.config import settings
import json
from typing import Optional, Any


class RedisClient:
    _instance: Optional[redis.Redis] = None
    
    @classmethod
    async def get_client(cls) -> redis.Redis:
        if cls._instance is None:
            cls._instance = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
            )
        return cls._instance
    
    @classmethod
    async def close(cls):
        if cls._instance:
            await cls._instance.close()
            cls._instance = None


async def get_redis() -> redis.Redis:
    return await RedisClient.get_client()


# Cache helpers
async def get_cache(key: str) -> Optional[Any]:
    client = await get_redis()
    value = await client.get(key)
    if value:
        return json.loads(value)
    return None


async def set_cache(key: str, value: Any, ttl: int):
    client = await get_redis()
    await client.setex(key, ttl, json.dumps(value))


# Rate limiting helpers (token bucket)
async def check_rate_limit(ip: str, requests_per_window: int, window_seconds: int) -> bool:
    """
    Token bucket rate limiting: 60 requests per 60 seconds
    Returns True if allowed, False if rate limited
    """
    client = await get_redis()
    key = f"rate_limit:{ip}"
    
    # Get current count
    current = await client.get(key)
    if current is None:
        # First request, set with window expiration
        await client.setex(key, window_seconds, 1)
        return True
    
    count = int(current)
    if count >= requests_per_window:
        return False
    
    # Increment counter
    await client.incr(key)
    return True
