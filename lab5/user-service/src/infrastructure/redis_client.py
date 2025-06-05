import os
import json
from typing import Optional, Any
import redis.asyncio as redis


class RedisClient:
    """Redis клиент для кеширования"""
    
    def __init__(self):
        self.redis: Optional[redis.Redis] = None
    
    async def connect(self):
        """Установить соединение с Redis"""
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.redis = redis.from_url(
            redis_url,
            encoding="utf-8",
            decode_responses=True
        )
        # Проверяем соединение
        await self.redis.ping()
    
    async def disconnect(self):
        """Закрыть соединение с Redis"""
        if self.redis:
            await self.redis.close()
    
    async def get(self, key: str) -> Optional[str]:
        """Получить значение из кеша"""
        if self.redis:
            return await self.redis.get(key)
        return None
    
    async def set(self, key: str, value: str, expire: Optional[int] = None):
        """Установить значение в кеш"""
        if self.redis:
            await self.redis.set(key, value, ex=expire)
    
    async def delete(self, key: str):
        """Удалить ключ из кеша"""
        if self.redis:
            await self.redis.delete(key)
    
    async def get_json(self, key: str) -> Optional[dict]:
        """Получить JSON объект из кеша"""
        value = await self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return None
        return None
    
    async def set_json(self, key: str, value: dict, expire: Optional[int] = None):
        """Установить JSON объект в кеш"""
        json_str = json.dumps(value, default=str)
        await self.set(key, json_str, expire)
    
    async def clear_pattern(self, pattern: str):
        """Удалить все ключи по паттерну"""
        if self.redis:
            keys = await self.redis.keys(pattern)
            if keys:
                await self.redis.delete(*keys)


# Глобальный экземпляр Redis клиента
redis_client = RedisClient()


async def get_redis_client() -> RedisClient:
    """Dependency для получения Redis клиента"""
    return redis_client 