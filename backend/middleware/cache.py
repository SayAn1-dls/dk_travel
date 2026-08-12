"""In-memory cache middleware for FastAPI."""

import hashlib
import json
import time
from typing import Any, Dict, Optional, Tuple

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from backend.config.constants import CACHE_TTL_SHORT


class CacheEntry:
    """Single cache entry with TTL."""

    def __init__(self, data: Any, ttl: int):
        self.data = data
        self.created_at = time.time()
        self.ttl = ttl

    @property
    def is_expired(self) -> bool:
        return time.time() - self.created_at > self.ttl

    @property
    def age(self) -> int:
        return int(time.time() - self.created_at)


class InMemoryCache:
    """Simple in-memory cache with TTL support.

    Suitable for single-instance deployments.
    For distributed systems, use Redis.
    """

    def __init__(self, max_entries: int = 1000, default_ttl: int = CACHE_TTL_SHORT):
        self._store: Dict[str, CacheEntry] = {}
        self.max_entries = max_entries
        self.default_ttl = default_ttl
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        entry = self._store.get(key)
        if entry is None:
            self._misses += 1
            return None
        if entry.is_expired:
            del self._store[key]
            self._misses += 1
            return None
        self._hits += 1
        return entry.data

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set a value in cache."""
        if len(self._store) >= self.max_entries:
            self._evict_expired()
            if len(self._store) >= self.max_entries:
                oldest_key = min(self._store, key=lambda k: self._store[k].created_at)
                del self._store[oldest_key]

        self._store[key] = CacheEntry(value, ttl or self.default_ttl)

    def delete(self, key: str) -> bool:
        """Delete a key from cache."""
        if key in self._store:
            del self._store[key]
            return True
        return False

    def clear(self) -> None:
        """Clear all cache entries."""
        self._store.clear()
        self._hits = 0
        self._misses = 0

    def _evict_expired(self) -> int:
        """Remove all expired entries."""
        expired = [k for k, v in self._store.items() if v.is_expired]
        for key in expired:
            del self._store[key]
        return len(expired)

    @property
    def stats(self) -> Dict[str, Any]:
        """Cache statistics."""
        total = self._hits + self._misses
        return {
            "entries": len(self._store),
            "max_entries": self.max_entries,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(self._hits / total * 100, 1) if total else 0,
        }


# Global cache instance
cache = InMemoryCache()


def _make_cache_key(request: Request) -> str:
    """Generate a cache key from the request."""
    parts = f"{request.method}:{request.url.path}:{str(request.query_params)}"
    return hashlib.md5(parts.encode()).hexdigest()


class CacheMiddleware(BaseHTTPMiddleware):
    """HTTP response cache middleware.

    Only caches GET requests. Skips caching for authenticated
    or mutation endpoints.
    """

    SKIP_PATHS = {"/docs", "/openapi.json", "/health", "/ping"}

    def __init__(self, app, ttl: int = CACHE_TTL_SHORT):
        super().__init__(app)
        self.ttl = ttl

    async def dispatch(self, request: Request, call_next) -> Response:
        """Check cache before processing request."""
        if request.method != "GET":
            return await call_next(request)

        if request.url.path in self.SKIP_PATHS:
            return await call_next(request)

        if request.headers.get("Authorization"):
            return await call_next(request)

        cache_key = _make_cache_key(request)
        cached = cache.get(cache_key)

        if cached is not None:
            response = Response(
                content=json.dumps(cached["body"]),
                status_code=cached["status_code"],
                media_type="application/json",
            )
            response.headers["X-Cache"] = "HIT"
            return response

        response = await call_next(request)

        if response.status_code == 200:
            body = b""
            async for chunk in response.body_iterator:
                body += chunk if isinstance(chunk, bytes) else chunk.encode()

            try:
                body_json = json.loads(body)
                cache.set(cache_key, {
                    "body": body_json,
                    "status_code": response.status_code,
                }, self.ttl)
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass

            new_response = Response(
                content=body,
                status_code=response.status_code,
                media_type=response.media_type,
            )
            new_response.headers["X-Cache"] = "MISS"
            return new_response

        return response
