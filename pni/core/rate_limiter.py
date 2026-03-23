"""Per-source rate limiter with exponential backoff retry."""

from __future__ import annotations

import asyncio
import time


class RateLimiter:
    """Token-bucket style rate limiter for async requests."""

    def __init__(self, requests_per_second: float = 1.0, max_retries: int = 3, base_delay: float = 1.0):
        self.min_interval = 1.0 / requests_per_second
        self.max_retries = max_retries
        self.base_delay = base_delay
        self._last_request: float = 0.0
        self._lock = asyncio.Lock()

    async def acquire(self):
        """Wait until a request is allowed."""
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_request
            if elapsed < self.min_interval:
                await asyncio.sleep(self.min_interval - elapsed)
            self._last_request = time.monotonic()

    async def execute_with_retry(self, coro_factory, *args, **kwargs):
        """Execute an async callable with retry and backoff."""
        last_exc = None
        for attempt in range(self.max_retries + 1):
            try:
                await self.acquire()
                return await coro_factory(*args, **kwargs)
            except Exception as e:
                last_exc = e
                if attempt < self.max_retries:
                    delay = self.base_delay * (2 ** attempt)
                    await asyncio.sleep(delay)
        raise last_exc
