"""Search engine dork queries for phone numbers — ported from phone_osint_v4.py."""

from __future__ import annotations

import re
import urllib.parse

import aiohttp

from pni.core.models import Query, QueryType, SourceResult
from pni.core.source import Source
from pni.modules.phone.analyzer import PhoneAnalyzer

HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0"}


def _clean(text: str, maxlen: int = 300) -> str:
    if not text:
        return ""
    return re.sub(r"\s+", " ", text.strip())[:maxlen]


def _build_dork_queries(analyzer: PhoneAnalyzer, max_queries: int = 20) -> list[str]:
    """Generate dork queries with strict variant scoping."""
    intl = analyzer.global_variants
    nat = analyzer.national_variants
    queries: list[str] = []

    # Bare global exact-match — international only
    for fmt in intl:
        queries.append(f'"{ fmt }"')

    # Platform dorks — international only
    for fmt in intl:
        queries += [
            f'"{ fmt }" site:facebook.com',
            f'"{ fmt }" site:linkedin.com',
            f'"{ fmt }" site:twitter.com OR site:x.com',
            f'"{ fmt }" site:reddit.com',
            f'"{ fmt }" site:pastebin.com',
            f'"{ fmt }" site:truecaller.com',
            f'"{ fmt }" spam OR scam OR fraud OR threat',
            f'"{ fmt }" contact OR email OR whatsapp',
            f'"{ fmt }" filetype:pdf',
            f'"{ fmt }" filetype:xlsx OR filetype:csv',
        ]

    # National variants — only with country-scoped keywords
    region = analyzer.region.lower() if analyzer.region != "Unknown" else ""
    for fmt in nat:
        queries += [
            f'"{ fmt }" site:{region}' if region else f'"{ fmt }"',
            f'"{ fmt }" phone number',
            f'"{ fmt }" spam OR scam',
        ]

    return list(dict.fromkeys(queries))[:max_queries]


async def _scrape_ddg(session: aiohttp.ClientSession, query: str) -> list[dict]:
    """Scrape DuckDuckGo HTML results."""
    from bs4 import BeautifulSoup

    encoded = urllib.parse.quote_plus(query)
    url = f"https://html.duckduckgo.com/html/?q={encoded}"
    try:
        async with session.get(url, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
    except Exception:
        return []

    soup = BeautifulSoup(html, "lxml")
    results = []
    for result in soup.select(".result")[:5]:
        title_el = result.select_one(".result__title")
        snippet_el = result.select_one(".result__snippet")
        link_el = result.select_one(".result__url")
        title = _clean(title_el.get_text() if title_el else "")
        snippet = _clean(snippet_el.get_text() if snippet_el else "")
        link = _clean(link_el.get_text() if link_el else "")
        if title or snippet:
            results.append({"title": title, "url": link, "snippet": snippet})
    return results


class PhoneDorkSource(Source):
    """Search engine dorking for phone numbers via DuckDuckGo."""

    def __init__(self, max_queries: int = 15, delay: float = 1.5):
        self.max_queries = max_queries
        self.delay = delay

    @property
    def name(self) -> str:
        return "Search Engine Dorks"

    @property
    def category(self) -> str:
        return "search"

    def supported_types(self) -> list[QueryType]:
        return [QueryType.PHONE]

    async def fetch(self, query: Query) -> list[SourceResult]:
        import asyncio

        analyzer = PhoneAnalyzer(query.value)
        dork_queries = _build_dork_queries(analyzer, self.max_queries)
        results: list[SourceResult] = []

        async with aiohttp.ClientSession() as session:
            for q in dork_queries:
                hits = await _scrape_ddg(session, q)
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
