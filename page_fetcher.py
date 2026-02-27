import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

PAGES = [
    "",
    "/contact",
    "/contact-us",
    "/about",
    "/about-us",
    "/impressum",
]

HEADERS = {"User-Agent": "Mozilla/5.0"}
TIMEOUT = 8


def fetch_pages(base_url: str) -> dict[str, BeautifulSoup]:
    """
    Fetch standard company pages and return parsed HTML.
    Only includes pages that returned HTTP 200.
    """
    results = {}
    for path in PAGES:
        try:
            page_url = urljoin(base_url, path)
            r = requests.get(page_url, headers=HEADERS, timeout=TIMEOUT)
            if r.status_code == 200:
                results[path] = BeautifulSoup(r.text, "html.parser")
        except Exception:
            continue
    return results
