"""Email breach and leak database lookups."""

from __future__ import annotations

import urllib.parse

import aiohttp

from pni.core.models import Query, QueryType, SourceResult
from pni.core.source import Source

HEADERS = {"User-Agent": "PNI-OSINT/0.1"}


class EmailBreachSource(Source):
    """Check email against breach databases and search engines for leaks."""

    def __init__(self, delay: float = 1.5):
        self.delay = delay

    @property
    def name(self) -> str:
        return "Email Breach Check"

    @property
    def category(self) -> str:
        return "breach"

    def supported_types(self) -> list[QueryType]:
        return [QueryType.EMAIL]

    async def fetch(self, query: Query) -> list[SourceResult]:
        import asyncio
        results: list[SourceResult] = []
        email = query.value

        async with aiohttp.ClientSession() as session:
            results.append(await self._check_hibp(session, email))
            await asyncio.sleep(self.delay)
            results.append(await self._search_pastes(session, email))
            await asyncio.sleep(self.delay)
            results.append(await self._search_breach_context(session, email))

        return results

    async def _check_hibp(self, session: aiohttp.ClientSession, email: str) -> SourceResult:
        """Check Have I Been Pwned API."""
        url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{urllib.parse.quote(email)}"
        try:
            async with session.get(
                url,
                headers={"User-Agent": "PNI-OSINT", "hibp-api-key": ""},
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    breaches = [{"name": b.get("Name"), "date": b.get("BreachDate"),
                                 "count": b.get("PwnCount")} for b in data[:10]]
                    return SourceResult(
                        "HIBP", "breach", "found", url=f"https://haveibeenpwned.com/account/{email}",
                        title=f"{len(data)} breaches found",
                        data={"breaches": breaches, "total": len(data)},
                    )
                elif resp.status == 404:
                    return SourceResult("HIBP", "breach", "not_found",
                                        title="No breaches found", url=url)
                elif resp.status == 401:
                    return SourceResult("HIBP", "breach", "error",
                                        title="API key required for full access", url=url)
                return SourceResult("HIBP", "breach", "error",
                                    title=f"HTTP {resp.status}", url=url)
        except Exception as e:
            return SourceResult("HIBP", "breach", "error", title=str(e), url=url)

    async def _search_pastes(self, session: aiohttp.ClientSession, email: str) -> SourceResult:
        """Search paste sites for the email."""
        from bs4 import BeautifulSoup

        q = f'"{ email }" site:pastebin.com OR site:paste.ee OR site:dpaste.com'
        url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote_plus(q)}"
        try:
            async with session.get(url, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    return SourceResult("Paste Search", "breach", "error", url=url)
                soup = BeautifulSoup(await resp.text(), "lxml")
                hits = []
                for r in soup.select(".result")[:5]:
                    t = r.select_one(".result__title")
                    u = r.select_one(".result__url")
                    s = r.select_one(".result__snippet")
                    if t:
                        hits.append({
                            "title": t.get_text().strip()[:200],
                            "url": u.get_text().strip() if u else "",
                            "snippet": s.get_text().strip()[:200] if s else "",
                        })
                status = "found" if hits else "not_found"
                return SourceResult("Paste Search", "breach", status, url=url,
                                    title=f"{len(hits)} paste results", data={"results": hits})
        except Exception as e:
            return SourceResult("Paste Search", "breach", "error", title=str(e), url=url)

    async def _search_breach_context(self, session: aiohttp.ClientSession, email: str) -> SourceResult:
        """Search for email in breach/leak contexts."""
        from bs4 import BeautifulSoup

        q = f'"{ email }" breach OR leak OR dump OR exposed'
        url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote_plus(q)}"
        try:
            async with session.get(url, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    return SourceResult("Breach Context", "breach", "error", url=url)
                soup = BeautifulSoup(await resp.text(), "lxml")
                hits = []
                for r in soup.select(".result")[:5]:
                    t = r.select_one(".result__title")
                    s = r.select_one(".result__snippet")
                    if t:
                        hits.append({
                            "title": t.get_text().strip()[:200],
                            "snippet": s.get_text().strip()[:200] if s else "",
                        })
                status = "found" if hits else "not_found"
                return SourceResult("Breach Context Search", "breach", status, url=url,
                                    title=f"{len(hits)} results", data={"results": hits})
        except Exception as e:
            return SourceResult("Breach Context Search", "breach", "error", title=str(e), url=url)
