"""Name parsing, normalization, and username generation."""

from __future__ import annotations

import re
import unicodedata
from typing import Any


class NameAnalyzer:
    """Offline name analysis — parsing, normalization, username generation."""

    def __init__(self, name: str):
        self.raw = name.strip()
        self._parts = self.raw.split()

    @property
    def normalized(self) -> str:
        return re.sub(r"\s+", " ", self.raw.strip().lower())

    @property
    def first_name(self) -> str:
        return self._parts[0] if self._parts else ""

    @property
    def last_name(self) -> str:
        return self._parts[-1] if len(self._parts) > 1 else ""

    @property
    def middle_parts(self) -> list[str]:
        return self._parts[1:-1] if len(self._parts) > 2 else []

    @property
    def ascii_name(self) -> str:
        nfkd = unicodedata.normalize("NFKD", self.raw)
        return "".join(c for c in nfkd if not unicodedata.combining(c))

    def username_variants(self) -> list[str]:
        first = self.first_name.lower()
        last = self.last_name.lower()
        if not first:
            return [self.normalized.replace(" ", "")]
        variants = [first]
        if last:
            variants += [
                f"{first}{last}", f"{first}.{last}", f"{first}_{last}",
                f"{first}-{last}", f"{last}{first}", f"{last}.{first}",
                f"{first[0]}{last}", f"{first}{last[0]}",
                f"{last}{first[0]}", f"{first[0]}.{last}",
            ]
        return list(dict.fromkeys(variants))

    def search_variants(self) -> list[str]:
        variants = [f'"{ self.raw }"']
        ascii_ver = self.ascii_name
        if ascii_ver != self.raw:
            variants.append(f'"{ ascii_ver }"')
        if self.first_name and self.last_name:
            variants.append(f'"{ self.last_name }, { self.first_name }"')
        return variants

    def to_dict(self) -> dict[str, Any]:
        return {
            "raw": self.raw, "normalized": self.normalized,
            "first_name": self.first_name, "last_name": self.last_name,
            "middle_parts": self.middle_parts, "ascii_name": self.ascii_name,
            "username_variants": self.username_variants(),
            "search_variants": self.search_variants(),
        }
