import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urlparse, parse_qs, unquote

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

BLOCKED_DOMAINS = [
    "linkedin.com",
    "facebook.com",
    "wikipedia.org",
    "crunchbase.com",
    "bloomberg.com",
    "zoominfo.com",
    "apollo.io"
]


def is_blocked_domain(url: str) -> bool:
    return any(domain in url for domain in BLOCKED_DOMAINS)


def clean_url(url: str) -> str:
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def find_website(company_name: str) -> str | None:
    query = quote_plus(f"{company_name} official website")
    search_url = f"https://duckduckgo.com/html/?q={query}"

    try:
        r = requests.get(search_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        results = soup.find_all("a", class_="result__a")

        for result in results[:5]:  # נבדוק עד 5 תוצאות
            href = result.get("href")
            if not href:
                continue

            parsed = urlparse(href)
            qs = parse_qs(parsed.query)

            if "uddg" in qs:
                candidate = unquote(qs["uddg"][0])
            else:
                candidate = href

            if not candidate.startswith("http"):
                continue

            if is_blocked_domain(candidate):
                continue

            return clean_url(candidate)

        return None

    except Exception:
        return None



