"""Local email analysis source — offline validation and metadata."""

from __future__ import annotations

from pni.core.models import Query, QueryType, SourceResult
from pni.core.source import Source
from pni.modules.email.analyzer import EmailAnalyzer


class EmailLocalSource(Source):
    """Offline email analysis — syntax, domain classification, username patterns."""

    @property
    def name(self) -> str:
        return "Email Local Analysis"

    @property
    def category(self) -> str:
        return "analysis"

    def supported_types(self) -> list[QueryType]:
        return [QueryType.EMAIL]

    async def fetch(self, query: Query) -> list[SourceResult]:
        try:
            analyzer = EmailAnalyzer(query.value)
            info = analyzer.to_dict()
            mx = analyzer.check_mx()
            info["mx_records"] = mx

            status = "found" if analyzer.is_valid_syntax else "not_found"
            title_parts = [analyzer.provider_type]
            if analyzer.is_disposable:
                title_parts.append("DISPOSABLE")
            if mx:
                title_parts.append("MX valid")

            return [SourceResult(
                source_name=self.name,
                category=self.category,
                status=status,
                data=info,
                title=" / ".join(title_parts),
                confidence=1.0 if analyzer.is_valid_syntax and mx else 0.5,
            )]
        except Exception as e:
            return [SourceResult(
                source_name=self.name, category=self.category,
                status="error", title=str(e),
            )]
