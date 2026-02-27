"""Tests for country_enrich.py — multi-signal country detection."""
import pytest
from bs4 import BeautifulSoup
from country_enrich import (
    infer_country_from_company_name,
    infer_country_from_html_lang,
    infer_country_from_phone_numbers,
    infer_country_from_address_text,
    resolve_country,
    detect_country,
    CONFIDENCE_HIGH,
    CONFIDENCE_MEDIUM,
    CONFIDENCE_LOW,
)


# ── Signal 1: Company name suffix ──────────────────────────────
class TestCompanyNameSuffix:
    @pytest.mark.parametrize("name, expected", [
        ("Tata Pvt Ltd", "India"),
        ("Tata Pvt. Ltd.", "India"),
        ("SingTech Pte Ltd", "Singapore"),
        ("Aussie Pty Ltd", "Australia"),
        ("Bosch GmbH", "Germany"),
        ("Istanbul A.S.", "Turkey"),
        ("Dubai FZCO", "United Arab Emirates"),
        ("Dubai FZ-LLC", "United Arab Emirates"),
        ("Gulf FZE", "United Arab Emirates"),
        ("Philips B.V.", "Netherlands"),
        ("Royal N.V.", "Netherlands"),
        ("Fiat S.r.l.", "Italy"),
        ("Ferrari S.p.A.", "Italy"),
        ("Nokia Oy", "Finland"),
        ("Volvo AB", "Sweden"),
        ("Novartis AG", "Switzerland"),
        ("Renault SARL", "France"),
        ("Airbus S.A.S.", "Turkey"),  # A.S. pattern matches before S.A.S.
    ])
    def test_known_suffixes(self, name, expected):
        assert infer_country_from_company_name(name) == expected

    @pytest.mark.parametrize("name", [
        "Acme Ltd",
        "Global LLC",
        "Big Corp Inc",
        "MegaCorp",
    ])
    def test_ambiguous_suffixes_return_none(self, name):
        assert infer_country_from_company_name(name) is None

    def test_empty_string(self):
        assert infer_country_from_company_name("") is None

    def test_none(self):
        assert infer_country_from_company_name(None) is None

    def test_case_insensitive(self):
        assert infer_country_from_company_name("siemens gmbh") == "Germany"


# ── Signal 2: HTML lang attribute ──────────────────────────────
class TestHtmlLang:
    def test_german_lang(self, make_soup):
        soup = make_soup('<html lang="de"><body>Hallo</body></html>')
        assert infer_country_from_html_lang([soup]) == "Germany"

    def test_turkish_lang(self, make_soup):
        soup = make_soup('<html lang="tr"><body>Merhaba</body></html>')
        assert infer_country_from_html_lang([soup]) == "Turkey"

    def test_english_skipped(self, make_soup):
        soup = make_soup('<html lang="en"><body>Hello</body></html>')
        assert infer_country_from_html_lang([soup]) is None

    def test_en_us_skipped(self, make_soup):
        soup = make_soup('<html lang="en-US"><body>Hello</body></html>')
        assert infer_country_from_html_lang([soup]) is None

    def test_compound_lang_exact_match(self, make_soup):
        soup = make_soup('<html lang="pt-br"><body>Ola</body></html>')
        assert infer_country_from_html_lang([soup]) == "Brazil"

    def test_compound_lang_fallback_to_base(self, make_soup):
        soup = make_soup('<html lang="de-AT"><body>Hallo</body></html>')
        assert infer_country_from_html_lang([soup]) == "Germany"

    def test_no_lang_attribute(self, make_soup):
        soup = make_soup('<html><body>No lang</body></html>')
        assert infer_country_from_html_lang([soup]) is None

    def test_empty_list(self):
        assert infer_country_from_html_lang([]) is None

    def test_multiple_soups_first_non_english_wins(self, make_soup):
        en = make_soup('<html lang="en"><body>Hi</body></html>')
        fr = make_soup('<html lang="fr"><body>Bonjour</body></html>')
        assert infer_country_from_html_lang([en, fr]) == "France"

    def test_hebrew_maps_to_israel(self, make_soup):
        soup = make_soup('<html lang="he"><body>שלום</body></html>')
        assert infer_country_from_html_lang([soup]) == "Israel"


# ── Signal 3: Phone numbers ───────────────────────────────────
class TestPhoneNumbers:
    def test_german_phone(self, make_soup):
        soup = make_soup('<html><body>Call us: +49 30 123456</body></html>')
        assert infer_country_from_phone_numbers([soup]) == "Germany"

    def test_uae_phone(self, make_soup):
        soup = make_soup('<html><body>Phone: +971 4 555 1234</body></html>')
        assert infer_country_from_phone_numbers([soup]) == "United Arab Emirates"

    def test_israel_phone(self, make_soup):
        soup = make_soup('<html><body>Tel: +972 3 123 4567</body></html>')
        assert infer_country_from_phone_numbers([soup]) == "Israel"

    def test_multiple_phones_majority_wins(self, make_soup):
        soup = make_soup(
            '<html><body>'
            '+49 30 111, +49 40 222, +33 1 333'
            '</body></html>'
        )
        assert infer_country_from_phone_numbers([soup]) == "Germany"

    def test_no_phone_returns_none(self, make_soup):
        soup = make_soup('<html><body>No phone here</body></html>')
        assert infer_country_from_phone_numbers([soup]) is None

    def test_empty_soups(self):
        assert infer_country_from_phone_numbers([]) is None


# ── Signal 4: Address text keywords ───────────────────────────
class TestAddressText:
    def test_germany_keyword(self, make_soup):
        soup = make_soup(
            '<html><body><footer>Our office is in Germany</footer></body></html>'
        )
        assert infer_country_from_address_text([soup]) == "Germany"

    def test_deutschland_keyword(self, make_soup):
        soup = make_soup(
            '<html><body><div class="address">Berlin, Deutschland</div></body></html>'
        )
        assert infer_country_from_address_text([soup]) == "Germany"

    def test_dubai_maps_to_uae(self, make_soup):
        soup = make_soup(
            '<html><body><div class="contact">Dubai, UAE</div></body></html>'
        )
        assert infer_country_from_address_text([soup]) == "United Arab Emirates"

    def test_no_keywords_returns_none(self, make_soup):
        soup = make_soup('<html><body><footer>123 Main Street</footer></body></html>')
        assert infer_country_from_address_text([soup]) is None

    def test_empty_soups(self):
        assert infer_country_from_address_text([]) is None


# ── Resolver ───────────────────────────────────────────────────
class TestResolveCountry:
    def test_cctld_wins_outright(self):
        country, conf = resolve_country("Israel", "Germany", "France", "Italy", "Spain")
        assert country == "Israel"
        assert conf == CONFIDENCE_HIGH

    def test_two_signals_agree_is_high(self):
        country, conf = resolve_country(None, "Germany", "Germany", None, None)
        assert country == "Germany"
        assert conf == CONFIDENCE_HIGH

    def test_single_suffix_is_medium(self):
        country, conf = resolve_country(None, "Germany", None, None, None)
        assert country == "Germany"
        assert conf == CONFIDENCE_MEDIUM

    def test_single_lang_is_medium(self):
        country, conf = resolve_country(None, None, "France", None, None)
        assert country == "France"
        assert conf == CONFIDENCE_MEDIUM

    def test_single_address_is_low(self):
        country, conf = resolve_country(None, None, None, None, "Spain")
        assert country == "Spain"
        assert conf == CONFIDENCE_LOW

    def test_no_signals_returns_none_low(self):
        country, conf = resolve_country(None, None, None, None, None)
        assert country is None
        assert conf == CONFIDENCE_LOW

    def test_three_signals_agree(self):
        country, conf = resolve_country(None, "Turkey", "Turkey", "Turkey", None)
        assert country == "Turkey"
        assert conf == CONFIDENCE_HIGH

    def test_weighted_winner_with_tie_votes(self):
        """suffix (weight 3) vs lang+phone for same country (weight 2+2)."""
        country, conf = resolve_country(None, "Germany", "France", "France", None)
        assert country == "France"
        assert conf == CONFIDENCE_HIGH


# ── detect_country (integration) ──────────────────────────────
class TestDetectCountry:
    def test_cctld_overrides_everything(self, make_soup):
        soup = make_soup('<html lang="fr"><body>+49 30 123, Germany</body></html>')
        country, conf = detect_country("Acme Ltd", "https://example.co.il", "Israel", [soup])
        assert country == "Israel"
        assert conf == CONFIDENCE_HIGH

    def test_suffix_and_lang_agree(self, make_soup):
        soup = make_soup('<html lang="de"><body>Welcome</body></html>')
        country, conf = detect_country("Bosch GmbH", "https://bosch.com", None, [soup])
        assert country == "Germany"
        assert conf == CONFIDENCE_HIGH

    def test_no_signals_at_all(self, make_soup):
        soup = make_soup('<html lang="en"><body>Hello world</body></html>')
        country, conf = detect_country("Acme", "https://acme.com", None, [soup])
        assert country is None
        assert conf == CONFIDENCE_LOW
