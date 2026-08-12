"""Redis-based caching middleware."""
import json
import hashlib
import logging
from typing import Optional, Any
from functools import wraps

logger = logging.getLogger(__name__)


class CacheMiddleware:
    """Redis cache layer for API responses."""

    def __init__(self, redis_client, default_ttl: int = 300):
        self.redis = redis_client
        self.default_ttl = default_ttl
        self._hit_count = 0
        self._miss_count = 0

    async def get(self, key: str) -> Optional[Any]:
        """Retrieve cached value."""
        try:
            value = await self.redis.get(key)
            if value:
                self._hit_count += 1
                return json.loads(value)
            self._miss_count += 1
            return None
        except Exception as e:
            logger.warning(f"Cache get error: {e}")
            return None

    async def set(
        self, key: str, value: Any, ttl: Optional[int] = None
    ) -> bool:
        """Store value in cache."""
        try:
            serialized = json.dumps(value, default=str)
            await self.redis.setex(
                key, ttl or self.default_ttl, serialized
            )
            return True
        except Exception as e:
            logger.warning(f"Cache set error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Remove cached value."""
        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Cache delete error: {e}")
            return False

    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching a pattern."""
        keys = await self.redis.keys(pattern)
        if keys:
            return await self.redis.delete(*keys)
        return 0

    def get_stats(self) -> dict:
        """Return cache hit/miss statistics."""
        total = self._hit_count + self._miss_count
        return {
            "hits": self._hit_count,
            "misses": self._miss_count,
            "hit_rate": self._hit_count / total if total > 0 else 0,
            "total_requests": total,
        }

    @staticmethod
    def cache_key(*args, **kwargs) -> str:
        """Generate deterministic cache key from arguments."""
        raw = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True, default=str)
        return f"cache:{hashlib.md5(raw.encode()).hexdigest()}"


def cached(ttl: int = 300):
    """Decorator to cache function results."""
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            if not hasattr(self, 'cache') or self.cache is None:
                return await func(self, *args, **kwargs)
            key = CacheMiddleware.cache_key(func.__name__, *args, **kwargs)
            result = await self.cache.get(key)
            if result is not None:
                return result
            result = await func(self, *args, **kwargs)
            await self.cache.set(key, result, ttl=ttl)
            return result
        return wrapper
    return decorator
