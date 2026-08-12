"""Rate limiting middleware for API protection."""
import time
import logging
from collections import defaultdict
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RateLimit:
    requests: int
    window_seconds: int
    burst: int = 0


class RateLimiter:
    """Token bucket rate limiter."""

    # Default rate limits per endpoint category
    DEFAULTS = {
        "auth": RateLimit(requests=5, window_seconds=60),
        "search": RateLimit(requests=30, window_seconds=60),
        "booking": RateLimit(requests=10, window_seconds=60),
        "general": RateLimit(requests=60, window_seconds=60),
    }

    def __init__(self, redis_client=None):
        self.redis = redis_client
        self._local_store: dict = defaultdict(list)

    async def is_allowed(
        self,
        client_id: str,
        endpoint_category: str = "general",
    ) -> bool:
        """Check if request is within rate limits."""
        limit = self.DEFAULTS.get(
            endpoint_category, self.DEFAULTS["general"]
        )
        key = f"ratelimit:{client_id}:{endpoint_category}"

        if self.redis:
            return await self._check_redis(key, limit)
        return self._check_local(key, limit)

    async def _check_redis(self, key: str, limit: RateLimit) -> bool:
        """Check rate limit using Redis."""
        try:
            current = await self.redis.incr(key)
            if current == 1:
                await self.redis.expire(key, limit.window_seconds)
            return current <= limit.requests
        except Exception as e:
            logger.error(f"Redis rate limit error: {e}")
            return True  # Fail open

    def _check_local(self, key: str, limit: RateLimit) -> bool:
        """Check rate limit using in-memory store."""
        now = time.time()
        window_start = now - limit.window_seconds

        # Clean old entries
        self._local_store[key] = [
            t for t in self._local_store[key] if t > window_start
        ]

        if len(self._local_store[key]) >= limit.requests:
            return False

        self._local_store[key].append(now)
        return True

    async def get_remaining(
        self, client_id: str, endpoint_category: str = "general"
    ) -> dict:
        """Get remaining requests info."""
        limit = self.DEFAULTS.get(
            endpoint_category, self.DEFAULTS["general"]
        )
        key = f"ratelimit:{client_id}:{endpoint_category}"

        if self.redis:
            current = await self.redis.get(key) or 0
            ttl = await self.redis.ttl(key)
        else:
            now = time.time()
            window_start = now - limit.window_seconds
            entries = [t for t in self._local_store[key] if t > window_start]
            current = len(entries)
            ttl = limit.window_seconds

        return {
            "limit": limit.requests,
            "remaining": max(0, limit.requests - int(current)),
            "reset_in_seconds": max(0, ttl),
        }

    async def reset(self, client_id: str, endpoint_category: str = "general"):
        """Reset rate limit for a client."""
        key = f"ratelimit:{client_id}:{endpoint_category}"
        if self.redis:
            await self.redis.delete(key)
        else:
            self._local_store.pop(key, None)
