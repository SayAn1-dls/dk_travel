"""Rate limiting middleware for FastAPI."""

import time
from collections import defaultdict
from typing import Dict, Tuple

from fastapi import HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from backend.config.constants import RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW_SECONDS


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """In-memory rate limiter using sliding window.

    Limits requests per client IP within a configurable time window.
    Suitable for single-instance deployments. For distributed systems,
    consider using Redis-based rate limiting.
    """

    def __init__(
        self,
        app,
        max_requests: int = RATE_LIMIT_REQUESTS,
        window_seconds: int = RATE_LIMIT_WINDOW_SECONDS,
    ):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # Store: {client_ip: [(timestamp, ...)]}
        self._requests: Dict[str, list] = defaultdict(list)

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request, handling proxies."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _clean_old_requests(self, client_ip: str, now: float) -> None:
        """Remove requests outside the current window."""
        cutoff = now - self.window_seconds
        self._requests[client_ip] = [
            ts for ts in self._requests[client_ip] if ts > cutoff
        ]

    def _get_rate_limit_info(self, client_ip: str) -> Tuple[int, int, float]:
        """Get rate limit info for a client.

        Returns:
            Tuple of (remaining_requests, total_limit, reset_time)
        """
        now = time.time()
        self._clean_old_requests(client_ip, now)

        current_count = len(self._requests[client_ip])
        remaining = max(0, self.max_requests - current_count)
        reset_time = now + self.window_seconds

        return remaining, self.max_requests, reset_time

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request with rate limiting."""
        # Skip rate limiting for health check endpoints
        if request.url.path in ("/health", "/ping", "/docs", "/openapi.json"):
            return await call_next(request)

        client_ip = self._get_client_ip(request)
        now = time.time()

        self._clean_old_requests(client_ip, now)
        current_count = len(self._requests[client_ip])

        if current_count >= self.max_requests:
            remaining, limit, reset_time = self._get_rate_limit_info(client_ip)
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "limit": limit,
                    "remaining": 0,
                    "retry_after": int(reset_time - now),
                },
            )

        self._requests[client_ip].append(now)

        response = await call_next(request)

        remaining, limit, reset_time = self._get_rate_limit_info(client_ip)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(reset_time))

        return response
