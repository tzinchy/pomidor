from app.main import app
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from app.core.config import settings


@app.on_event("startup")
async def startup():
    redis = aioredis.from_url(settings.redis.REDIS_HOST, encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="dashboard-cache")

@app.on_event("redis-test")
async def redis_test():
    redis = aioredis.from_url(settings.redis.REDIS_HOST)
    try:
        await redis.ping()
        print("✅ Успешное подключение к Redis")
    except Exception as e:
        print(f"❌ Ошибка подключения к Redis: {str(e)}")
    FastAPICache.init(RedisBackend(redis), prefix="dashboard-cache")

