"""Local name analysis source."""

from __future__ import annotations

from pni.core.models import Query, QueryType, SourceResult
from pni.core.source import Source
from pni.modules.name.analyzer import NameAnalyzer


class NameLocalSource(Source):
    """Offline name parsing, normalization, and username generation."""

    @property
    def name(self) -> str:
        return "Name Local Analysis"

    @property
    def category(self) -> str:
        return "analysis"

    def supported_types(self) -> list[QueryType]:
        return [QueryType.NAME]

    async def fetch(self, query: Query) -> list[SourceResult]:
        try:
            analyzer = NameAnalyzer(query.value)
            info = analyzer.to_dict()
            return [SourceResult(
                source_name=self.name,
                category=self.category,
                status="found",
                data=info,
                title=f"{analyzer.first_name} {analyzer.last_name}".strip(),
                confidence=1.0,
            )]
        except Exception as e:
            return [SourceResult(
                source_name=self.name, category=self.category,
                status="error", title=str(e),
            )]
