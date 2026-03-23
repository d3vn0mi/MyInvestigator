"""Phone number parsing, validation, and local analysis using the phonenumbers library."""

from __future__ import annotations

import phonenumbers
from phonenumbers import geocoder, carrier, timezone


class PhoneAnalyzer:
    """Offline phone number analysis — no network calls."""

    TYPE_MAP = {
        0: "Fixed Line", 1: "Mobile", 2: "Fixed or Mobile", 3: "Toll Free",
        4: "Premium Rate", 5: "Shared Cost", 6: "VoIP", 7: "Personal",
        8: "Pager", 9: "UAN", 10: "Voicemail", -1: "Unknown",
    }

    def __init__(self, raw_number: str, default_region: str | None = None):
        self.raw = raw_number
        self.parsed = phonenumbers.parse(raw_number, default_region)

    @property
    def is_valid(self) -> bool:
        return phonenumbers.is_valid_number(self.parsed)

    @property
    def e164(self) -> str:
        return phonenumbers.format_number(self.parsed, phonenumbers.PhoneNumberFormat.E164)

    @property
    def international(self) -> str:
        return phonenumbers.format_number(self.parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)

    @property
    def national(self) -> str:
        return phonenumbers.format_number(self.parsed, phonenumbers.PhoneNumberFormat.NATIONAL)

    @property
    def digits(self) -> str:
        return "".join(filter(str.isdigit, self.e164))

    @property
    def region(self) -> str:
        return phonenumbers.region_code_for_number(self.parsed) or "Unknown"

    @property
    def country_code(self) -> str:
        return str(self.parsed.country_code)

    @property
    def carrier_name(self) -> str:
        return carrier.name_for_number(self.parsed, "en") or "Unknown"

    @property
    def line_type(self) -> str:
        return self.TYPE_MAP.get(phonenumbers.number_type(self.parsed), "Unknown")

    @property
    def location(self) -> str:
        return geocoder.description_for_number(self.parsed, "en") or "Unknown"

    @property
    def timezones(self) -> list[str]:
        return list(timezone.time_zones_for_number(self.parsed))

    @property
    def global_variants(self) -> list[str]:
        """International variants — safe for global searches."""
        return list(dict.fromkeys([
            self.e164,
            self.international,
            self.international.replace(" ", "-"),
            self.raw.replace("+", "00"),
            self.digits,
        ]))

    @property
    def national_variants(self) -> list[str]:
        """National variants — only safe with country-scoped queries."""
        nat = self.national
        return list(dict.fromkeys([
            nat,
            nat.replace(" ", ""),
            nat.replace(" ", "-"),
            nat.replace(" ", "."),
        ]))

    def to_dict(self) -> dict:
        return {
            "raw": self.raw,
            "e164": self.e164,
            "international": self.international,
            "national": self.national,
            "digits": self.digits,
            "region": self.region,
            "country_code": self.country_code,
            "carrier": self.carrier_name,
            "line_type": self.line_type,
            "location": self.location,
            "timezones": self.timezones,
            "valid": self.is_valid,
            "global_variants": self.global_variants,
            "national_variants": self.national_variants,
        }
