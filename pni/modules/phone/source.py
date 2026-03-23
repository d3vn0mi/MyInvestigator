"""Local (offline) phone analysis source."""

from __future__ import annotations

from pni.core.models import Query, QueryType, SourceResult
from pni.core.source import Source
from pni.modules.phone.analyzer import PhoneAnalyzer


class PhoneLocalSource(Source):
    """Offline phone number analysis using the phonenumbers library."""

    @property
    def name(self) -> str:
        return "Phone Local Analysis"

    @property
    def category(self) -> str:
        return "analysis"

    def supported_types(self) -> list[QueryType]:
        return [QueryType.PHONE]

    async def fetch(self, query: Query) -> list[SourceResult]:
        try:
            analyzer = PhoneAnalyzer(query.value)
            info = analyzer.to_dict()
            return [SourceResult(
                source_name=self.name,
                category=self.category,
                status="found" if analyzer.is_valid else "not_found",
                data=info,
                title=f"{info['carrier']} / {info['line_type']} / {info['location']}",
                confidence=1.0 if analyzer.is_valid else 0.0,
            )]
        except Exception as e:
            return [SourceResult(
                source_name=self.name, category=self.category,
                status="error", title=str(e),
            )]
