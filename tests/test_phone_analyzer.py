"""Tests for phone number analyzer."""

import pytest
from pni.modules.phone.analyzer import PhoneAnalyzer


def test_parse_valid_us_number():
    a = PhoneAnalyzer("+14155552671")
    assert a.is_valid
    assert a.e164 == "+14155552671"
    assert a.region == "US"
    assert a.country_code == "1"


def test_parse_valid_nl_number():
    a = PhoneAnalyzer("+31645161166")
    assert a.is_valid
    assert a.region == "NL"
    assert a.country_code == "31"


def test_line_type():
    a = PhoneAnalyzer("+14155552671")
    assert a.line_type in PhoneAnalyzer.TYPE_MAP.values()


def test_global_variants_contain_e164():
    a = PhoneAnalyzer("+14155552671")
    assert a.e164 in a.global_variants


def test_national_variants():
    a = PhoneAnalyzer("+31645161166")
    variants = a.national_variants
    assert len(variants) > 0
    for v in variants:
        assert "+" not in v


def test_to_dict_keys():
    a = PhoneAnalyzer("+14155552671")
    d = a.to_dict()
    expected_keys = {"raw", "e164", "international", "national", "digits", "region",
                     "country_code", "carrier", "line_type", "location", "timezones",
                     "valid", "global_variants", "national_variants"}
    assert expected_keys == set(d.keys())


def test_invalid_number_raises():
    with pytest.raises(Exception):
        PhoneAnalyzer("not-a-number")
