"""Central investigation orchestrator."""

from __future__ import annotations

import asyncio

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

from pni.core.models import Query, InvestigationResult, SourceResult
from pni.core.source import Source
from pni.core.cache import Cache

console = Console()


class Investigator:
    """Dispatches queries to registered sources and collects results."""

    def __init__(self, sources: list[Source] | None = None, cache: Cache | None = None):
        self._sources: list[Source] = sources or []
        self._cache = cache

    def register(self, source: Source):
        self._sources.append(source)

    async def investigate(self, query: Query, show_progress: bool = True) -> InvestigationResult:
        """Run all matching sources against the query."""
        matching = [s for s in self._sources if s.supports(query.query_type)]

        if not matching:
            console.print(f"[yellow]No sources registered for {query.query_type.value}[/yellow]")
            return InvestigationResult(query=query)

        # Check cache first
        cache_key = f"{query.query_type.value}:{query.value}"
        if self._cache:
            cached = await self._cache.get(cache_key)
            if cached:
                console.print(f"[dim]Using cached results for {query.value}[/dim]")
                return InvestigationResult(
                    query=query,
                    results=[
                        SourceResult(
                            source_name=r.get("source", r.get("source_name", "")),
                            category=r.get("category", ""),
                            status=r.get("status", ""),
                            data=r.get("data", {}),
                            url=r.get("url", ""),
                            title=r.get("title", ""),
                            snippet=r.get("snippet", ""),
                            confidence=r.get("confidence", 0.0),
                            timestamp=r.get("timestamp", ""),
                        )
                        for r in cached["results"]
                    ],
                    timestamp=cached.get("timestamp", ""),
                )

        all_results: list[SourceResult] = []

        if show_progress:
            with Progress(
                SpinnerColumn(),
                TextColumn("{task.description}"),
                BarColumn(),
                console=console,
            ) as progress:
                task = progress.add_task(
                    f"[cyan]Running {len(matching)} sources...", total=len(matching)
                )
                for source in matching:
                    progress.update(task, description=f"[cyan]{source.name}...")
                    try:
                        results = await asyncio.wait_for(
                            source.fetch(query), timeout=30.0
                        )
                        all_results.extend(results)
                        status_color = "green" if any(r.status == "found" for r in results) else "dim"
                        progress.update(
                            task,
                            description=f"[{status_color}]{source.name}: done[/{status_color}]",
                        )
                    except asyncio.TimeoutError:
                        all_results.append(SourceResult(
                            source_name=source.name, category=source.category,
                            status="error", title="Timeout",
                        ))
                    except Exception as e:
                        all_results.append(SourceResult(
                            source_name=source.name, category=source.category,
                            status="error", title=str(e),
                        ))
                    progress.advance(task)
        else:
            for source in matching:
                try:
                    results = await asyncio.wait_for(source.fetch(query), timeout=30.0)
                    all_results.extend(results)
                except Exception as e:
                    all_results.append(SourceResult(
                        source_name=source.name, category=source.category,
                        status="error", title=str(e),
                    ))

        result = InvestigationResult(query=query, results=all_results)

        # Cache results
        if self._cache:
            await self._cache.set(cache_key, result.to_dict())

        return result
