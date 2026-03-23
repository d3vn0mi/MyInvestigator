"""Social media username enumeration for name-based investigations."""

from __future__ import annotations

import aiohttp

from pni.core.models import Query, QueryType, SourceResult
from pni.core.source import Source
from pni.modules.name.analyzer import NameAnalyzer

HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0"}

PLATFORMS = {
    "GitHub": "https://github.com/{}",
    "Twitter/X": "https://x.com/{}",
    "Instagram": "https://www.instagram.com/{}/",
    "Reddit": "https://www.reddit.com/user/{}/",
    "LinkedIn": "https://www.linkedin.com/in/{}/",
    "Pinterest": "https://www.pinterest.com/{}/",
    "Medium": "https://medium.com/@{}",
    "DevTo": "https://dev.to/{}",
    "Keybase": "https://keybase.io/{}",
}


class NameSocialSource(Source):
    """Enumerate potential social media profiles from name-derived usernames."""

    def __init__(self, delay: float = 0.5, max_usernames: int = 5):
        self.delay = delay
        self.max_usernames = max_usernames

    @property
    def name(self) -> str:
        return "Social Media Enumeration"

    @property
    def category(self) -> str:
        return "social"

    def supported_types(self) -> list[QueryType]:
        return [QueryType.NAME]

    async def fetch(self, query: Query) -> list[SourceResult]:
        import asyncio

        analyzer = NameAnalyzer(query.value)
        usernames = analyzer.username_variants()[:self.max_usernames]
        results: list[SourceResult] = []

        async with aiohttp.ClientSession() as session:
            for username in usernames:
                platform_hits = []
                for platform, url_template in PLATFORMS.items():
                    url = url_template.format(username)
                    try:
                        async with session.get(
                            url, headers=HEADERS,
                            timeout=aiohttp.ClientTimeout(total=8),
                            allow_redirects=True,
                        ) as resp:
                            if resp.status == 200:
                                platform_hits.append({
                                    "platform": platform,
                                    "url": url,
                                    "username": username,
                                    "status": resp.status,
                                })
                    except Exception:
                        pass
                    await asyncio.sleep(self.delay)

                if platform_hits:
                    results.append(SourceResult(
                        source_name=self.name,
                        category=self.category,
                        status="found",
                        title=f"@{username}: {len(platform_hits)} platforms",
                        data={"username": username, "platforms": platform_hits},
                    ))

        if not results:
            results.append(SourceResult(
                source_name=self.name, category=self.category,
                status="not_found", title="No social profiles found",
            ))

        return results
