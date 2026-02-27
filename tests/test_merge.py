"""Tests for merge helper functions across merge modules."""
import pytest
from merge_by_domain import extract_domain as domain_extract_domain
from merge_emails import normalize_company, normalize_email


# ── extract_domain (merge_by_domain.py) ────────────────────────
class TestExtractDomain:
    def test_basic_url(self):
        assert domain_extract_domain("https://www.example.com/about") == "example.com"

    def test_strips_www(self):
        assert domain_extract_domain("https://www.siemens.com") == "siemens.com"

    def test_no_www(self):
        assert domain_extract_domain("https://siemens.de") == "siemens.de"

    def test_http_scheme(self):
        assert domain_extract_domain("http://www.test.com") == "test.com"

    def test_none_returns_none(self):
        assert domain_extract_domain(None) is None

    def test_int_returns_none(self):
        assert domain_extract_domain(123) is None

    def test_empty_string(self):
        # urlparse("") returns empty netloc and empty path
        result = domain_extract_domain("")
        assert result is None or result == ""


# ── normalize_company ──────────────────────────────────────────
class TestNormalizeCompany:
    def test_basic(self):
        assert normalize_company("Acme Corp") == "acme corp"

    def test_replaces_ampersand(self):
        assert normalize_company("A & B") == "a and b"

    def test_removes_dots(self):
        assert normalize_company("A.B.C.") == "abc"

    def test_removes_commas(self):
        assert normalize_company("Acme, Inc") == "acme inc"

    def test_strips_whitespace(self):
        assert normalize_company("  Acme  ") == "acme"

    def test_non_string_returns_empty(self):
        assert normalize_company(None) == ""
        assert normalize_company(123) == ""

    def test_combined(self):
        assert normalize_company("  A & B., Ltd.  ") == "a and b ltd"


# ── normalize_email ────────────────────────────────────────────
class TestNormalizeEmail:
    def test_basic(self):
        assert normalize_email("User@Example.COM") == "user@example.com"

    def test_strips_whitespace(self):
        assert normalize_email("  info@co.com  ") == "info@co.com"

    def test_none_returns_none(self):
        assert normalize_email(None) is None

    def test_int_returns_none(self):
        assert normalize_email(123) is None
