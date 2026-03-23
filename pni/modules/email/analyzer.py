"""Email address parsing, validation, and domain analysis."""

from __future__ import annotations

import re
import socket
from typing import Any


class EmailAnalyzer:
    """Offline email analysis — validation, domain info, pattern extraction."""

    EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")

    DISPOSABLE_DOMAINS = {
        "tempmail.com", "throwaway.email", "guerrillamail.com", "mailinator.com",
        "yopmail.com", "10minutemail.com", "trashmail.com", "fakeinbox.com",
        "sharklasers.com", "guerrillamailblock.com", "grr.la", "dispostable.com",
        "maildrop.cc", "temp-mail.org", "getnada.com",
    }

    def __init__(self, email: str):
        self.raw = email.strip().lower()
        parts = self.raw.split("@")
        self.local_part = parts[0] if len(parts) == 2 else ""
        self.domain = parts[1] if len(parts) == 2 else ""

    @property
    def is_valid_syntax(self) -> bool:
        return bool(self.EMAIL_RE.match(self.raw))

    @property
    def is_disposable(self) -> bool:
        return self.domain in self.DISPOSABLE_DOMAINS

    @property
    def provider_type(self) -> str:
        freemail = {"gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
                    "protonmail.com", "aol.com", "icloud.com", "mail.com",
                    "zoho.com", "yandex.com", "gmx.com", "live.com"}
        if self.domain in freemail:
            return "free"
        if self.is_disposable:
            return "disposable"
        return "business/custom"

    def check_mx(self) -> list[str]:
        try:
            import dns.resolver
            answers = dns.resolver.resolve(self.domain, "MX")
            return [str(r.exchange) for r in answers]
        except Exception:
            try:
                socket.getaddrinfo(self.domain, 25)
                return [f"{self.domain} (A record)"]
            except Exception:
                return []

    def username_variants(self) -> list[str]:
        base = self.local_part
        variants = [base]
        if "." in base:
            variants.append(base.replace(".", ""))
        if "+" in base:
            variants.append(base.split("+")[0])
        if "." in base:
            parts = base.split(".")
            if len(parts) == 2:
                variants.append(f"{parts[1]}{parts[0]}")
                variants.append(f"{parts[0]}_{parts[1]}")
                variants.append(f"{parts[0]}-{parts[1]}")
        return list(dict.fromkeys(variants))

    def to_dict(self) -> dict[str, Any]:
        return {
            "raw": self.raw,
            "local_part": self.local_part,
            "domain": self.domain,
            "valid_syntax": self.is_valid_syntax,
            "disposable": self.is_disposable,
            "provider_type": self.provider_type,
            "username_variants": self.username_variants(),
        }
