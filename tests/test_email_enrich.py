"""Tests for email_enrich.py — email extraction and selection."""
import pytest
from bs4 import BeautifulSoup
from email_enrich import select_best_email, extract_email_from_soups


# ── select_best_email ──────────────────────────────────────────
class TestSelectBestEmail:
    def test_prefers_info_at(self):
        emails = {"sales@co.com", "info@co.com", "john@co.com"}
        assert select_best_email(emails) == "info@co.com"

    def test_prefers_contact_at(self):
        emails = {"random@co.com", "contact@co.com"}
        assert select_best_email(emails) == "contact@co.com"

    def test_prefers_sales_at(self):
        emails = {"random@co.com", "sales@co.com"}
        assert select_best_email(emails) == "sales@co.com"

    def test_prefers_office_at(self):
        emails = {"random@co.com", "office@co.com"}
        assert select_best_email(emails) == "office@co.com"

    def test_prefers_hello_at(self):
        emails = {"random@co.com", "hello@co.com"}
        assert select_best_email(emails) == "hello@co.com"

    def test_filters_out_noreply(self):
        emails = {"noreply@co.com", "real@co.com"}
        assert select_best_email(emails) == "real@co.com"

    def test_filters_out_test(self):
        emails = {"test@co.com", "real@co.com"}
        assert select_best_email(emails) == "real@co.com"

    def test_filters_out_example(self):
        emails = {"user@example.com", "real@co.com"}
        assert select_best_email(emails) == "real@co.com"

    def test_filters_no_reply_hyphenated(self):
        emails = {"no-reply@co.com", "real@co.com"}
        assert select_best_email(emails) == "real@co.com"

    def test_empty_set_returns_none(self):
        assert select_best_email(set()) is None

    def test_only_bad_emails_returns_none(self):
        emails = {"noreply@co.com", "test@co.com", "example@co.com"}
        assert select_best_email(emails) is None

    def test_no_preferred_returns_alphabetical_first(self):
        emails = {"zara@co.com", "adam@co.com"}
        assert select_best_email(emails) == "adam@co.com"


# ── extract_email_from_soups ───────────────────────────────────
class TestExtractEmailFromSoups:
    def test_extracts_from_text(self, make_soup):
        soup = make_soup('<html><body>Contact us at info@company.de</body></html>')
        assert extract_email_from_soups({"": soup}) == "info@company.de"

    def test_extracts_from_mailto(self, make_soup):
        soup = make_soup(
            '<html><body>'
            '<a href="mailto:contact@firm.com">Email us</a>'
            '</body></html>'
        )
        assert extract_email_from_soups({"": soup}) == "contact@firm.com"

    def test_mailto_with_query_params(self, make_soup):
        soup = make_soup(
            '<html><body>'
            '<a href="mailto:hi@site.com?subject=Hello">Mail</a>'
            '</body></html>'
        )
        assert extract_email_from_soups({"": soup}) == "hi@site.com"

    def test_prefers_info_over_random(self, make_soup):
        soup = make_soup(
            '<html><body>'
            'Reach us at random@co.com or info@co.com'
            '</body></html>'
        )
        assert extract_email_from_soups({"": soup}) == "info@co.com"

    def test_multiple_pages(self, make_soup):
        home = make_soup('<html><body>No emails here</body></html>')
        contact = make_soup('<html><body>Email: sales@firm.de</body></html>')
        assert extract_email_from_soups({"": home, "/contact": contact}) == "sales@firm.de"

    def test_no_emails_returns_none(self, make_soup):
        soup = make_soup('<html><body>Nothing to see here</body></html>')
        assert extract_email_from_soups({"": soup}) is None

    def test_empty_soups_returns_none(self):
        assert extract_email_from_soups({}) is None

    def test_filters_bad_emails(self, make_soup):
        soup = make_soup(
            '<html><body>'
            'noreply@co.com and real@co.com'
            '</body></html>'
        )
        assert extract_email_from_soups({"": soup}) == "real@co.com"
