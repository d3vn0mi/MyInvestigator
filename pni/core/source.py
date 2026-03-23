"""Abstract base class for all data sources."""

from __future__ import annotations

from abc import ABC, abstractmethod

from pni.core.models import Query, QueryType, SourceResult


class Source(ABC):
    """Base class that every data source must implement."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable source name."""

    @property
    @abstractmethod
    def category(self) -> str:
        """Category: search, reputation, paste, social, api, etc."""

    @abstractmethod
    def supported_types(self) -> list[QueryType]:
        """Return the query types this source can handle."""

    @abstractmethod
    async def fetch(self, query: Query) -> list[SourceResult]:
        """Run the lookup and return results."""

    def supports(self, query_type: QueryType) -> bool:
        return query_type in self.supported_types()
