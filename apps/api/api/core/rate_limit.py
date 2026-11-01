"""
Manual per-user rate limiting for the AI-heavy endpoints.

Every call to PlantMind chat, plant lookup, recommendations, image analysis and the AI
"add plant" flow fans out to Groq (and often Tavily/Perenual) - metered, rate-limited
upstream APIs. Without a cap a single user (or a runaway client loop) can burn the whole
Groq quota and take the feature down for everyone.

How it works: a sliding-window log per (user, bucket). Each bucket has several windows
(a short burst limit plus a longer hourly cap). A request over any window is rejected with
HTTP 429 and a Retry-After header; rejected requests are NOT recorded, so waiting out the
Retry-After is always enough.

Limits are enforced in process memory. That is exact on a single long-lived server (Render)
and best-effort on serverless (Vercel), where each warm instance keeps its own counters -
see docs/DEPLOYMENT.md. Set RATE_LIMIT_ENABLED=false to switch it off (e.g. local load tests).
"""
import math
import threading
import time
from collections import deque
from typing import Awaitable, Callable, Deque, Dict, Optional, Sequence, Tuple

from fastapi import Depends, HTTPException

from .auth import verify_firebase_token
from .config import settings

Window = Tuple[int, int]  # (max requests, window length in seconds)

# Per-user limits. Tune here. Each entry is [(burst per minute), (cap per hour)].
LIMITS: Dict[str, Sequence[Window]] = {
    "chat": [(10, 60), (120, 3600)],             # PlantMind chat messages (agent + tool calls)
    "lookup": [(8, 60), (60, 3600)],             # Explore: 2 Groq calls + 2 web searches each
    "recommendations": [(3, 60), (15, 3600)],    # a full agent pass per call
    "plant_create": [(6, 60), (40, 3600)],       # AI "add plant" (extraction + schedule)
    "vision": [(5, 60), (30, 3600)],             # image analysis and care-plan generation
}

_SWEEP_EVERY_SECONDS = 300


class SlidingWindowLimiter:
    def __init__(self, clock: Callable[[], float] = time.monotonic):
        self._clock = clock
        self._lock = threading.Lock()
        self._hits: Dict[Tuple[str, str], Tuple[Deque[float], int]] = {}
        self._last_sweep = clock()

    def check(self, key: str, bucket: str, windows: Sequence[Window]) -> Optional[int]:
        """
        Record a hit for `key` in `bucket`. Returns None when the request is allowed, or the
        whole number of seconds until it would be allowed when any window is full (in which
        case nothing is recorded).
        """
        now = self._clock()
        longest = max(seconds for _, seconds in windows)
        with self._lock:
            hits, _ = self._hits.setdefault((key, bucket), (deque(), longest))
            while hits and now - hits[0] >= longest:
                hits.popleft()

            wait = 0
            for limit, seconds in windows:
                recent = [t for t in hits if now - t < seconds]
                if len(recent) >= limit:
                    wait = max(wait, math.ceil(recent[0] + seconds - now))
            if wait:
                return max(wait, 1)

            hits.append(now)
            self._hits[(key, bucket)] = (hits, longest)
            self._sweep(now)
            return None

    def _sweep(self, now: float) -> None:
        """Drop idle users so the table can't grow without bound. Caller holds the lock."""
        if now - self._last_sweep < _SWEEP_EVERY_SECONDS:
            return
        self._last_sweep = now
        stale = [k for k, (hits, longest) in self._hits.items() if not hits or now - hits[-1] >= longest]
        for k in stale:
            del self._hits[k]

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()


limiter = SlidingWindowLimiter()


def _human_wait(seconds: int) -> str:
    if seconds < 60:
        return f"{seconds} second{'s' if seconds != 1 else ''}"
    minutes = math.ceil(seconds / 60)
    return f"{minutes} minute{'s' if minutes != 1 else ''}"


def ai_rate_limit(bucket: str) -> Callable[..., Awaitable[str]]:
    """
    FastAPI dependency factory. Drop-in replacement for `Depends(verify_firebase_token)` on an
    AI endpoint: it authenticates (same dependency, resolved once per request), enforces the
    bucket's limits for that user and returns the user id.
    """
    windows = LIMITS[bucket]

    async def dependency(user_id: str = Depends(verify_firebase_token)) -> str:
        if settings.RATE_LIMIT_ENABLED:
            wait = limiter.check(user_id, bucket, windows)
            if wait is not None:
                raise HTTPException(
                    status_code=429,
                    detail=f"You're going a little fast. Please wait {_human_wait(wait)} and try again.",
                    headers={"Retry-After": str(wait)},
                )
        return user_id

    return dependency


chat_limit = ai_rate_limit("chat")
lookup_limit = ai_rate_limit("lookup")
recommendations_limit = ai_rate_limit("recommendations")
plant_create_limit = ai_rate_limit("plant_create")
vision_limit = ai_rate_limit("vision")
