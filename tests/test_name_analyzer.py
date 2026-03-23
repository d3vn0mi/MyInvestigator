"""Tests for name analyzer."""

from pni.modules.name.analyzer import NameAnalyzer


def test_basic_parsing():
    a = NameAnalyzer("John Doe")
    assert a.first_name == "John"
    assert a.last_name == "Doe"
    assert a.normalized == "john doe"


def test_three_part_name():
    a = NameAnalyzer("John Michael Doe")
    assert a.first_name == "John"
    assert a.last_name == "Doe"
    assert a.middle_parts == ["Michael"]


def test_single_name():
    a = NameAnalyzer("Madonna")
    assert a.first_name == "Madonna"
    assert a.last_name == ""


def test_username_variants():
    a = NameAnalyzer("John Doe")
    variants = a.username_variants()
    assert "johndoe" in variants
    assert "john.doe" in variants
    assert "doejohn" in variants


def test_search_variants():
    a = NameAnalyzer("John Doe")
    variants = a.search_variants()
    assert '"John Doe"' in variants
    assert '"Doe, John"' in variants


def test_ascii_transliteration():
    a = NameAnalyzer("Jose Garcia")
    assert a.ascii_name == "Jose Garcia"


def test_to_dict():
    a = NameAnalyzer("Jane Smith")
    d = a.to_dict()
    assert "raw" in d
    assert "username_variants" in d
    assert "search_variants" in d
