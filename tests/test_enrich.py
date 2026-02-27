"""Tests for enrich.py — website discovery helpers."""
import pytest
from enrich import is_blocked_domain, clean_url


# ── is_blocked_domain ──────────────────────────────────────────
class TestIsBlockedDomain:
    @pytest.mark.parametrize("url", [
        "https://www.linkedin.com/company/acme",
        "https://facebook.com/acme",
        "https://en.wikipedia.org/wiki/Acme",
        "https://www.crunchbase.com/organization/acme",
        "https://bloomberg.com/profile/acme",
        "https://www.zoominfo.com/c/acme",
        "https://apollo.io/companies/acme",
    ])
    def test_blocked_domains_detected(self, url):
        assert is_blocked_domain(url) is True

    @pytest.mark.parametrize("url", [
        "https://www.siemens.com",
        "https://acme-corp.de",
        "https://example.co.il",
    ])
    def test_valid_domains_not_blocked(self, url):
        assert is_blocked_domain(url) is False

    def test_empty_string_not_blocked(self):
        assert is_blocked_domain("") is False


# ── clean_url ──────────────────────────────────────────────────
class TestCleanUrl:
    def test_strips_path(self):
        assert clean_url("https://example.com/about/team") == "https://example.com"

    def test_strips_query_params(self):
        assert clean_url("https://example.com?ref=search") == "https://example.com"

    def test_preserves_scheme(self):
        assert clean_url("http://example.com/page") == "http://example.com"

    def test_preserves_subdomain(self):
        assert clean_url("https://shop.example.com/products") == "https://shop.example.com"
