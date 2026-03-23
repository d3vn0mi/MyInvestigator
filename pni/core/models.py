"""Shared data models."""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class QueryType(Enum):
    PHONE = "phone"
    EMAIL = "email"
    NAME = "name"


@dataclass
class Query:
    query_type: QueryType
    value: str
    options: dict[str, Any] = field(default_factory=dict)


@dataclass
class SourceResult:
    source_name: str
    category: str
    status: str  # found | not_found | error
    data: dict[str, Any] = field(default_factory=dict)
    url: str = ""
    title: str = ""
    snippet: str = ""
    confidence: float = 0.0
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.datetime.now().isoformat()


@dataclass
class InvestigationResult:
    query: Query
    results: list[SourceResult] = field(default_factory=list)
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.datetime.now().isoformat()

    @property
    def found_count(self) -> int:
        return sum(1 for r in self.results if r.status == "found")

    @property
    def total_count(self) -> int:
        return len(self.results)

    def to_dict(self) -> dict:
        return {
            "query": {"type": self.query.query_type.value, "value": self.query.value},
            "timestamp": self.timestamp,
            "summary": {
                "total": self.total_count,
                "found": self.found_count,
            },
            "results": [
                {
                    "source": r.source_name,
                    "category": r.category,
                    "status": r.status,
                    "url": r.url,
                    "title": r.title,
                    "snippet": r.snippet,
                    "confidence": r.confidence,
                    "data": r.data,
                    "timestamp": r.timestamp,
                }
                for r in self.results
            ],
        }
