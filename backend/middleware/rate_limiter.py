"""Enterprise Rate Limiter Middleware for TravelPilot.

Supports in-memory sliding-window request throttling with optional Redis backing.
Protects auth, planning, and chat endpoints against denial-of-service, brute-force,
and token depletion attacks.
"""

import time
import logging
from typing import Dict, List, Tuple
from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("travelpilot.rate_limiter")

class RateLimitExceeded(HTTPException):
    def __init__(self, retry_after: int = 60, detail: str = "Rate limit exceeded. Please try again later."):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            headers={"Retry-After": str(retry_after)}
        )

class SlidingWindowLimiter:
    def __init__(self):
        # Maps (client_key, endpoint_category) -> list of timestamps
        self.history: Dict[Tuple[str, str], List[float]] = {}

    def is_allowed(self, client_key: str, category: str, max_requests: int, window_seconds: int = 60) -> Tuple[bool, int]:
        now = time.time()
        cutoff = now - window_seconds
        key = (client_key, category)

        timestamps = self.history.get(key, [])
        # Evict old timestamps
        timestamps = [t for t in timestamps if t > cutoff]
        self.history[key] = timestamps

        if len(timestamps) >= max_requests:
            oldest = timestamps[0]
            retry_after = max(1, int(cutoff + window_seconds - oldest))
            return False, retry_after

        timestamps.append(now)
        self.history[key] = timestamps
        return True, 0

limiter = SlidingWindowLimiter()

class RateLimiterMiddleware(BaseHTTPMiddleware):
    # Rule table: path_prefix -> (max_requests_per_minute, category_name)
    ENDPOINT_LIMITS = [
        ("/api/auth/login", (10, "auth_login")),
        ("/api/auth/register", (10, "auth_register")),
        ("/api/auth/send-otp", (5, "auth_otp")),
        ("/api/auth/verify-otp", (10, "auth_otp_verify")),
        ("/api/trips/", (8, "trip_planning")),  # matches /plan and /replan
        ("/api/chat", (25, "chat_assistant")),
    ]

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        path = request.url.path

        # Match specific endpoint rules
        for prefix, (limit, category) in self.ENDPOINT_LIMITS:
            if prefix in path and request.method in ["POST", "PUT"]:
                allowed, retry_after = limiter.is_allowed(client_ip, category, max_requests=limit, window_seconds=60)
                if not allowed:
                    logger.warning(f"Rate limit triggered for {client_ip} on {path} ({category})")
                    return Response(
                        content=f'{{"detail": "Rate limit exceeded for {category}. Please wait {retry_after}s before retrying."}}',
                        status_code=429,
                        media_type="application/json",
                        headers={"Retry-After": str(retry_after)}
                    )

        # Global safety baseline: max 150 requests / min per IP
        allowed, retry_after = limiter.is_allowed(client_ip, "global", max_requests=150, window_seconds=60)
        if not allowed:
            return Response(
                content=f'{{"detail": "Global request quota exceeded. Please wait {retry_after}s."}}',
                status_code=429,
                media_type="application/json",
                headers={"Retry-After": str(retry_after)}
            )

        response = await call_next(request)
        return response
