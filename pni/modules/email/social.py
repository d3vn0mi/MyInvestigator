"""Social media and platform discovery for email addresses."""

from __future__ import annotations

import hashlib
import urllib.parse

import aiohttp

from pni.core.models import Query, QueryType, SourceResult
from pni.core.source import Source

HEADERS = {"User-Agent": "PNI-OSINT/0.1"}


class EmailSocialSource(Source):
    """Discover social media accounts linked to an email."""

    def __init__(self, delay: float = 1.0):
        self.delay = delay

    @property
    def name(self) -> str:
        return "Email Social Discovery"

    @property
    def category(self) -> str:
        return "social"

    def supported_types(self) -> list[QueryType]:
        return [QueryType.EMAIL]

    async def fetch(self, query: Query) -> list[SourceResult]:
        import asyncio
        results: list[SourceResult] = []
        email = query.value.strip().lower()

        async with aiohttp.ClientSession() as session:
            results.append(await self._check_gravatar(session, email))
            await asyncio.sleep(self.delay)
            results.append(await self._check_github(session, email))
            await asyncio.sleep(self.delay)
            results.append(await self._search_social(session, email))
            await asyncio.sleep(self.delay)
            results.append(await self._search_platforms(session, email))

        return results

    async def _check_gravatar(self, session: aiohttp.ClientSession, email: str) -> SourceResult:
        email_hash = hashlib.md5(email.encode()).hexdigest()
        profile_url = f"https://gravatar.com/{email_hash}.json"
        try:
            async with session.get(profile_url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    entry = data.get("entry", [{}])[0] if data.get("entry") else {}
                    return SourceResult(
                        "Gravatar", "social", "found", url=profile_url,
                        title=entry.get("displayName", "Profile found"),
                        data={
                            "display_name": entry.get("displayName"),
                            "profile_url": entry.get("profileUrl"),
                            "about": entry.get("aboutMe"),
                            "location": entry.get("currentLocation"),
                            "photos": [p.get("value") for p in entry.get("photos", [])],
                            "accounts": [
                                {"platform": a.get("shortname"), "url": a.get("url")}
                                for a in entry.get("accounts", [])
                            ],
                        },
                    )
                return SourceResult("Gravatar", "social", "not_found", url=profile_url,
                                    title="No Gravatar profile")
        except Exception as e:
            return SourceResult("Gravatar", "social", "error", title=str(e), url=profile_url)

    async def _check_github(self, session: aiohttp.ClientSession, email: str) -> SourceResult:
        url = f"https://api.github.com/search/commits?q=author-email:{urllib.parse.quote(email)}&per_page=5"
        try:
            async with session.get(
                url, headers={"Accept": "application/vnd.github.cloak-preview+json"},
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    count = data.get("total_count", 0)
                    commits = []
                    for item in data.get("items", [])[:5]:
                        commits.append({
                            "repo": item.get("repository", {}).get("full_name"),
                            "message": item.get("commit", {}).get("message", "")[:100],
                            "author": item.get("commit", {}).get("author", {}).get("name"),
                            "url": item.get("html_url"),
                        })
                    if count > 0:
                        return SourceResult(
                            "GitHub", "social", "found", url=url,
                            title=f"{count} commits found",
                            data={"total_commits": count, "commits": commits},
                        )
                return SourceResult("GitHub", "social", "not_found", url=url,
                                    title="No GitHub commits found")
        except Exception as e:
            return SourceResult("GitHub", "social", "error", title=str(e), url=url)

    async def _search_social(self, session: aiohttp.ClientSession, email: str) -> SourceResult:
        from bs4 import BeautifulSoup
        q = f'"{ email }" site:twitter.com OR site:x.com OR site:instagram.com OR site:facebook.com'
        url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote_plus(q)}"
        try:
            async with session.get(url, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    return SourceResult("Social Search", "social", "error", url=url)
                soup = BeautifulSoup(await resp.text(), "lxml")
                hits = []
                for r in soup.select(".result")[:5]:
                    t = r.select_one(".result__title")
                    u = r.select_one(".result__url")
                    if t:
                        hits.append({"title": t.get_text().strip()[:200], "url": u.get_text().strip() if u else ""})
                status = "found" if hits else "not_found"
                return SourceResult("Social Search", "social", status, url=url,
                                    title=f"{len(hits)} social results", data={"results": hits})
        except Exception as e:
            return SourceResult("Social Search", "social", "error", title=str(e), url=url)

    async def _search_platforms(self, session: aiohttp.ClientSession, email: str) -> SourceResult:
        from bs4 import BeautifulSoup
        q = f'"{ email }" site:linkedin.com OR site:github.com OR site:about.me OR site:keybase.io'
        url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote_plus(q)}"
        try:
            async with session.get(url, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    return SourceResult("Platform Search", "social", "error", url=url)
                soup = BeautifulSoup(await resp.text(), "lxml")
                hits = []
                for r in soup.select(".result")[:5]:
                    t = r.select_one(".result__title")
                    u = r.select_one(".result__url")
                    if t:
                        hits.append({"title": t.get_text().strip()[:200], "url": u.get_text().strip() if u else ""})
                status = "found" if hits else "not_found"
                return SourceResult("Platform Search", "social", status, url=url,
                                    title=f"{len(hits)} platform results", data={"results": hits})
        except Exception as e:
            return SourceResult("Platform Search", "social", "error", title=str(e), url=url)
