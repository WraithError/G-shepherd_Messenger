import redis.asyncio as aioredis

from app.core.config import settings

# Singleton Redis client — one connection pool shared across the app
redis_client: aioredis.Redis = aioredis.from_url(
    settings.REDIS_URL,
    encoding="utf-8",
    decode_responses=True,
)


async def get_redis() -> aioredis.Redis:
    """FastAPI dependency — returns the shared Redis client."""
    return redis_client
