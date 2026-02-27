"""Shared fixtures for ICU enrichment agent tests."""
import sys, os
import pytest
from bs4 import BeautifulSoup

# Allow imports from the parent enrichment_agent directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture
def make_soup():
    """Factory fixture: build a BeautifulSoup from an HTML string."""
    def _make(html: str) -> BeautifulSoup:
        return BeautifulSoup(html, "html.parser")
    return _make
