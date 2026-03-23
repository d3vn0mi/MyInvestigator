"""Search engine queries for name investigation."""

from __future__ import annotations

import urllib.parse

import aiohttp
from bs4 import BeautifulSoup

from pni.core.models import Query, QueryType, SourceResult
from pni.core.source import Source
from pni.modules.name.analyzer import NameAnalyzer

HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0"}


async def _ddg_search(session: aiohttp.ClientSession, query: str) -> list[dict]:
    url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote_plus(query)}"
    try:
        async with session.get(url, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            if resp.status != 200:
                return []
            soup = BeautifulSoup(await resp.text(), "lxml")
            results = []
            for r in soup.select(".result")[:5]:
                t = r.select_one(".result__title")
                u = r.select_one(".result__url")
                s = r.select_one(".result__snippet")
                if t:
                    results.append({
                        "title": t.get_text().strip()[:200],
                        "url": u.get_text().strip() if u else "",
                        "snippet": s.get_text().strip()[:200] if s else "",
                    })
            return results
    except Exception:
        return []


class NameSearchSource(Source):
    """Search engines for name-related intelligence."""

    def __init__(self, max_queries: int = 10, delay: float = 1.5):
        self.max_queries = max_queries
        self.delay = delay

    @property
    def name(self) -> str:
        return "Name Search Engine"

    @property
    def category(self) -> str:
        return "search"

    def supported_types(self) -> list[QueryType]:
        return [QueryType.NAME]

    async def fetch(self, query: Query) -> list[SourceResult]:
        import asyncio

        analyzer = NameAnalyzer(query.value)
        search_queries = []

        for variant in analyzer.search_variants():
            search_queries += [
                variant,
                f"{variant} phone OR email OR contact",
                f"{variant} linkedin OR twitter OR facebook",
                f"{variant} site:linkedin.com",
                f"{variant} site:twitter.com OR site:x.com",
                f"{variant} site:facebook.com",
                f"{variant} site:github.com",
            ]

        search_queries = list(dict.fromkeys(search_queries))[:self.max_queries]
        results: list[SourceResult] = []

        async with aiohttp.ClientSession() as session:
            for q in search_queries:
                hits = await _ddg_search(session, q)
                results.append(SourceResult(
                    source_name=self.name,
                    category=self.category,
                    status="found" if hits else "not_found",
                    url=f"https://html.duckduckgo.com/html/?q={urllib.parse.quote_plus(q)}",
                    title=q,
                    data={"query": q, "results": hits},
                ))
                await asyncio.sleep(self.delay)

        return results
