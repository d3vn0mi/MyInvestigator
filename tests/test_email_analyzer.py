"""Tests for email analyzer."""

from pni.modules.email.analyzer import EmailAnalyzer


def test_valid_email():
    a = EmailAnalyzer("user@gmail.com")
    assert a.is_valid_syntax
    assert a.domain == "gmail.com"
    assert a.local_part == "user"


def test_invalid_email():
    a = EmailAnalyzer("not-an-email")
    assert not a.is_valid_syntax


def test_disposable_detection():
    a = EmailAnalyzer("test@mailinator.com")
    assert a.is_disposable
    assert a.provider_type == "disposable"


def test_free_provider():
    a = EmailAnalyzer("test@gmail.com")
    assert a.provider_type == "free"
    assert not a.is_disposable


def test_business_provider():
    a = EmailAnalyzer("ceo@acmecorp.com")
    assert a.provider_type == "business/custom"


def test_username_variants():
    a = EmailAnalyzer("john.doe@gmail.com")
    variants = a.username_variants()
    assert "john.doe" in variants
    assert "johndoe" in variants


def test_to_dict():
    a = EmailAnalyzer("user@example.com")
    d = a.to_dict()
    assert "raw" in d
    assert "domain" in d
    assert "valid_syntax" in d
