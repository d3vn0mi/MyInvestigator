"""SQLite-backed async cache for investigation results."""

from __future__ import annotations

import json
import os
import time

import aiosqlite

DEFAULT_DB_PATH = os.path.join(os.path.expanduser("~"), ".pni", "cache.db")


class Cache:
    """Async SQLite cache with TTL support."""

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        self._db: aiosqlite.Connection | None = None

    async def open(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._db = await aiosqlite.connect(self.db_path)
        await self._db.execute(
            "CREATE TABLE IF NOT EXISTS cache "
            "(key TEXT PRIMARY KEY, value TEXT, created_at REAL, ttl INTEGER)"
        )
        await self._db.commit()

    async def close(self):
        if self._db:
            await self._db.close()
            self._db = None

    async def get(self, key: str) -> dict | None:
        if not self._db:
            return None
        cursor = await self._db.execute(
            "SELECT value, created_at, ttl FROM cache WHERE key = ?", (key,)
        )
        row = await cursor.fetchone()
        if not row:
            return None
        value, created_at, ttl = row
        if ttl > 0 and (time.time() - created_at) > ttl:
            await self._db.execute("DELETE FROM cache WHERE key = ?", (key,))
            await self._db.commit()
            return None
        return json.loads(value)

    async def set(self, key: str, value: dict, ttl: int = 3600):
        if not self._db:
            return
        await self._db.execute(
            "INSERT OR REPLACE INTO cache (key, value, created_at, ttl) VALUES (?, ?, ?, ?)",
            (key, json.dumps(value, default=str), time.time(), ttl),
        )
        await self._db.commit()

    async def clear(self):
        if not self._db:
            return
        await self._db.execute("DELETE FROM cache")
        await self._db.commit()
