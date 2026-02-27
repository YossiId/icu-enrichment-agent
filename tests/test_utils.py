"""Tests for utils.py — ccTLD-based country inference."""
import pytest
from utils import infer_country_from_domain, CC_TLD_MAP, AMBIGUOUS_TLDS


# ── Direct ccTLD lookups ───────────────────────────────────────
class TestCcTldLookups:
    @pytest.mark.parametrize("domain, expected", [
        ("https://example.co.il", "Israel"),
        ("https://firma.de", "Germany"),
        ("https://site.fr", "France"),
        ("https://company.tr", "Turkey"),
        ("https://shop.jp", "Japan"),
        ("https://business.ae", "United Arab Emirates"),
        ("https://corp.sa", "Saudi Arabia"),
        ("https://service.in", "India"),
        ("https://brand.au", "Australia"),
        ("https://group.br", "Brazil"),
    ])
    def test_known_cctlds(self, domain, expected):
        assert infer_country_from_domain(domain) == expected

    @pytest.mark.parametrize("domain", [
        "https://example.com",
        "https://site.org",
        "https://app.net",
    ])
    def test_generic_tlds_return_none(self, domain):
        assert infer_country_from_domain(domain) is None


# ── Compound TLDs ──────────────────────────────────────────────
class TestCompoundTlds:
    @pytest.mark.parametrize("domain, expected", [
        ("https://example.co.uk", "United Kingdom"),
        ("https://shop.co.za", "South Africa"),
        ("https://site.co.nz", "New Zealand"),
        ("https://firm.co.kr", "South Korea"),
    ])
    def test_compound_tlds(self, domain, expected):
        assert infer_country_from_domain(domain) == expected


# ── Ambiguous TLDs ─────────────────────────────────────────────
class TestAmbiguousTlds:
    @pytest.mark.parametrize("domain", [
        "https://startup.io",
        "https://cool.ai",
        "https://portfolio.me",
        "https://stream.tv",
        "https://example.co",
    ])
    def test_ambiguous_tlds_return_none(self, domain):
        assert infer_country_from_domain(domain) is None


# ── Edge cases ─────────────────────────────────────────────────
class TestEdgeCases:
    def test_empty_string(self):
        assert infer_country_from_domain("") is None

    def test_none_input(self):
        assert infer_country_from_domain(None) is None

    def test_malformed_url(self):
        assert infer_country_from_domain("not-a-url") is None

    def test_with_www_prefix(self):
        assert infer_country_from_domain("https://www.example.de") == "Germany"

    def test_with_subdomain(self):
        assert infer_country_from_domain("https://shop.store.co.il") == "Israel"

    def test_all_map_entries_have_values(self):
        """Every entry in CC_TLD_MAP should map to a non-empty string."""
        for tld, country in CC_TLD_MAP.items():
            assert isinstance(country, str) and len(country) > 0, f"{tld} has bad value"

    def test_ambiguous_set_not_in_map(self):
        """Ambiguous TLDs must not appear in the country map."""
        for tld in AMBIGUOUS_TLDS:
            assert tld not in CC_TLD_MAP, f"{tld} is in both AMBIGUOUS and CC_TLD_MAP"
