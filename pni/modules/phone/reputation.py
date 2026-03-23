"""Phone reputation database scrapers — ported from phone_osint_v4.py."""

from __future__ import annotations

import re
import urllib.parse

import aiohttp
from bs4 import BeautifulSoup

from pni.core.models import Query, QueryType, SourceResult
from pni.core.source import Source
from pni.modules.phone.analyzer import PhoneAnalyzer

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36"}


def _clean(text: str, maxlen: int = 300) -> str:
    if not text:
        return ""
    return re.sub(r"\s+", " ", text.strip())[:maxlen]


async def _fetch_soup(session: aiohttp.ClientSession, url: str) -> BeautifulSoup | None:
    try:
        async with session.get(url, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            if resp.status != 200:
                return None
            return BeautifulSoup(await resp.text(), "lxml")
    except Exception:
        return None


async def _scrape_whocalledme(session: aiohttp.ClientSession, digits: str) -> SourceResult:
    url = f"https://whocalledme.com/PhoneNumber/{digits}"
    soup = await _fetch_soup(session, url)
    if not soup:
        return SourceResult("WhoCalledMe", "reputation", "error", url=url, title="Request failed")
    data = {}
    rating = soup.select_one(".rating-text, .call-type, h2")
    if rating:
        data["rating"] = _clean(rating.get_text())
    comments = soup.select(".comment-text, .report-text, p")
    snippets = [_clean(c.get_text()) for c in comments[:5] if len(c.get_text().strip()) > 20]
    data["comments"] = snippets
    status = "found" if data.get("rating") or snippets else "not_found"
    return SourceResult("WhoCalledMe", "reputation", status, url=url,
                        snippet=" | ".join(snippets[:2]), data=data)


async def _scrape_800notes(session: aiohttp.ClientSession, e164: str) -> SourceResult:
    url = f"https://800notes.com/Phone.aspx/{e164}"
    soup = await _fetch_soup(session, url)
    if not soup:
        return SourceResult("800notes", "reputation", "error", url=url)
    comments = soup.select(".msg-body, .comment, p.body")
    snippets = [_clean(c.get_text()) for c in comments[:5] if len(c.get_text().strip()) > 20]
    data = {"comments": snippets}
    title_el = soup.select_one("h1, .phone-title")
    if title_el:
        data["page_title"] = _clean(title_el.get_text())
    status = "found" if snippets else "not_found"
    return SourceResult("800notes", "reputation", status, url=url,
                        snippet=" | ".join(snippets[:2]), data=data)


async def _scrape_spamcalls(session: aiohttp.ClientSession, raw: str) -> SourceResult:
    enc = urllib.parse.quote_plus(raw)
    url = f"https://spamcalls.net/en/search?number={enc}"
    try:
        async with session.get(url, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            if resp.status != 200:
                return SourceResult("SpamCalls.net", "reputation", "error", url=url)
            text = await resp.text()
    except Exception:
        return SourceResult("SpamCalls.net", "reputation", "error", url=url)

    soup = BeautifulSoup(text, "lxml")
    comments = soup.select(".comment, .report, p")
    snippets = [_clean(c.get_text()) for c in comments[:5] if len(c.get_text().strip()) > 20]
    is_spam = any(x in text.lower() for x in ["spam", "scam", "fraud", "threat"])
    data = {"comments": snippets, "spam_signals": is_spam, "report_mentions": text.lower().count("report")}
    status = "found" if is_spam or snippets else "not_found"
    return SourceResult("SpamCalls.net", "reputation", status, url=url,
                        snippet=" | ".join(snippets[:2]), data=data)


async def _scrape_numlookup(session: aiohttp.ClientSession, digits: str) -> SourceResult:
    url = f"https://www.numlookup.com/number/{digits}"
    soup = await _fetch_soup(session, url)
    if not soup:
        return SourceResult("NumLookup.com", "reputation", "error", url=url)
    data = {}
    for row in soup.select("table tr, .info-row, .detail-row"):
        cells = row.select("td, th")
        if len(cells) >= 2:
            k = _clean(cells[0].get_text())
            v = _clean(cells[1].get_text())
            if k and v:
                data[k] = v
    status = "found" if data else "not_found"
    return SourceResult("NumLookup.com", "reputation", status, url=url, data=data)


async def _api_numlookup(session: aiohttp.ClientSession, e164: str) -> SourceResult:
    url = f"https://api.numlookupapi.com/v1/info/{urllib.parse.quote(e164)}"
    try:
        async with session.get(url, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            if resp.status == 200:
                d = await resp.json()
                return SourceResult("NumLookupAPI", "api", "found", url=url, data={
                    "valid": d.get("valid"), "carrier": d.get("carrier"),
                    "line_type": d.get("line_type"), "country": d.get("country_name"),
                    "location": d.get("location"), "local_fmt": d.get("local_format"),
                })
            return SourceResult("NumLookupAPI", "api", "error", url=url, title=f"HTTP {resp.status}")
    except Exception:
        return SourceResult("NumLookupAPI", "api", "error", url=url, title="Request failed")


class PhoneReputationSource(Source):
    """Aggregates results from multiple phone reputation databases."""

    def __init__(self, delay: float = 1.0):
        self.delay = delay

    @property
    def name(self) -> str:
        return "Phone Reputation DBs"

    @property
    def category(self) -> str:
        return "reputation"

    def supported_types(self) -> list[QueryType]:
        return [QueryType.PHONE]

    async def fetch(self, query: Query) -> list[SourceResult]:
        import asyncio

        analyzer = PhoneAnalyzer(query.value)
        results: list[SourceResult] = []

        async with aiohttp.ClientSession() as session:
            scrapers = [
                _scrape_whocalledme(session, analyzer.digits),
                _scrape_800notes(session, analyzer.e164),
                _scrape_spamcalls(session, analyzer.raw),
                _scrape_numlookup(session, analyzer.digits),
                _api_numlookup(session, analyzer.e164),
            ]
            for coro in scrapers:
                try:
                    result = await coro
                    results.append(result)
                except Exception as e:
                    results.append(SourceResult(
                        source_name="Reputation", category="reputation",
                        status="error", title=str(e),
                    ))
                await asyncio.sleep(self.delay)

        return results
