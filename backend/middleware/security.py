"""Security Headers, Request-ID, and Structured Latency Logging Middleware.
"""

import time
import uuid
import logging
import json
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("travelpilot.security")

MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB limit

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 1. Enforce payload size limit
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > MAX_CONTENT_LENGTH:
            return Response(
                content=json.dumps({"detail": "Payload too large. Maximum allowed size is 5MB."}),
                status_code=413,
                media_type="application/json"
            )

        # 2. Inject or propagate Request-ID
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        start_time = time.time()

        # Call next handler
        response = await call_next(request)

        # 3. Compute latency
        latency_ms = round((time.time() - start_time) * 1000, 2)

        # 4. Attach Security Headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Server-Timing"] = f"total;dur={latency_ms}"

        # 5. Structured Log
        logger.info(
            json.dumps({
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "latency_ms": latency_ms,
                "client_ip": request.client.host if request.client else "unknown"
            })
        )

        return response
