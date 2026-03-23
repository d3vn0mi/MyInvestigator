"""Wayback Machine (Internet Archive) integration for all query types."""

from __future__ import annotations

import urllib.parse

import aiohttp

from pni.core.models import Query, QueryType, SourceResult
from pni.core.source import Source

CDX_API = "https://web.archive.org/cdx/search/cdx"
HEADERS = {"User-Agent": "PNI-OSINT/0.1 (Internet Archive research)"}


class WaybackSource(Source):
    """Search the Wayback Machine CDX API for archived pages mentioning the target."""

    def __init__(self, max_results: int = 20, delay: float = 1.0):
        self.max_results = max_results
        self.delay = delay

    @property
    def name(self) -> str:
        return "Wayback Machine"

    @property
    def category(self) -> str:
        return "archive"

    def supported_types(self) -> list[QueryType]:
        return [QueryType.PHONE, QueryType.EMAIL, QueryType.NAME]

    async def fetch(self, query: Query) -> list[SourceResult]:
        import asyncio
        results: list[SourceResult] = []

        search_terms = self._build_search_terms(query)

        async with aiohttp.ClientSession() as session:
            for term in search_terms:
                cdx_results = await self._search_cdx(session, term)
                if cdx_results:
                    results.append(SourceResult(
                        source_name=self.name,
                        category=self.category,
                        status="found",
                        title=f"Wayback CDX: {len(cdx_results)} archived pages",
                        url=f"https://web.archive.org/web/*/{term}",
                        data={"term": term, "archives": cdx_results},
                    ))
                await asyncio.sleep(self.delay)

                ft_results = await self._fulltext_search(session, term)
                if ft_results:
                    results.append(SourceResult(
                        source_name=f"{self.name} (Full-text)",
                        category=self.category,
                        status="found",
                        title=f"Full-text search: {len(ft_results)} results",
                        url=f"https://web.archive.org/web/*/{term}",
                        data={"term": term, "pages": ft_results},
                    ))
                await asyncio.sleep(self.delay)

        if not results:
            results.append(SourceResult(
                source_name=self.name, category=self.category,
                status="not_found", title="No Wayback Machine results",
            ))

        return results

    def _build_search_terms(self, query: Query) -> list[str]:
        value = query.value
        if query.query_type == QueryType.PHONE:
            digits = "".join(filter(str.isdigit, value))
            return [value, digits]
        elif query.query_type == QueryType.EMAIL:
            return [value]
        elif query.query_type == QueryType.NAME:
            return [value]
        return [value]

    async def _search_cdx(self, session: aiohttp.ClientSession, term: str) -> list[dict]:
        params = {
            "url": f"*/*{urllib.parse.quote(term)}*",
            "output": "json",
            "limit": str(self.max_results),
            "fl": "timestamp,original,mimetype,statuscode",
            "filter": "statuscode:200",
        }
        try:
            async with session.get(
                CDX_API, params=params, headers=HEADERS,
                timeout=aiohttp.ClientTimeout(total=15),
            ) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json(content_type=None)
                if not data or len(data) < 2:
                    return []
                headers_row = data[0]
                results = []
                for row in data[1:self.max_results + 1]:
                    entry = dict(zip(headers_row, row))
                    entry["wayback_url"] = f"https://web.archive.org/web/{entry.get('timestamp', '')}/{entry.get('original', '')}"
                    results.append(entry)
                return results
        except Exception:
            return []

    async def _fulltext_search(self, session: aiohttp.ClientSession, term: str) -> list[dict]:
        url = f"https://web.archive.org/__wb/search/anchor?q={urllib.parse.quote(term)}&limit={self.max_results}"
        try:
            async with session.get(
                url, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=15),
            ) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json(content_type=None)
                if not data:
                    return []
                results = []
                for item in data[:self.max_results]:
                    if isinstance(item, dict):
                        results.append({
                            "url": item.get("url", ""),
                            "title": item.get("title", ""),
                            "snippet": item.get("snippet", "")[:300],
                        })
                    elif isinstance(item, str):
                        results.append({"url": item})
                return results
        except Exception:
            return []
