"""
In-memory rate limiter for public endpoints (e.g. API key registration).
Not distributed: resets on app restart. Sufficient for single-instance deploy.
"""
import time
from collections import defaultdict
from fastapi import Request, HTTPException, status

# ip -> list of request timestamps (within window)
_store: dict[str, list[float]] = defaultdict(list)
WINDOW_SECONDS = 3600  # 1 hour
MAX_REQUESTS_PER_WINDOW = 5


def get_client_ip(request: Request) -> str:
    """Prefer X-Forwarded-For when behind proxy (Cloudflare, Railway)."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


def check_rate_limit(request: Request) -> None:
    """Raises 429 if IP has exceeded MAX_REQUESTS_PER_WINDOW in WINDOW_SECONDS."""
    ip = get_client_ip(request)
    now = time.monotonic()
    # Use monotonic for relative TTL; store (monotonic_start, timestamp) or just timestamps
    # Simple: store time.time() and expire entries older than WINDOW_SECONDS
    cutoff = time.time() - WINDOW_SECONDS
    _store[ip] = [t for t in _store[ip] if t > cutoff]
    if len(_store[ip]) >= MAX_REQUESTS_PER_WINDOW:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many API key requests. Try again later.",
        )
    _store[ip].append(time.time())
