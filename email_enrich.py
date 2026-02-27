import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

PAGES = [
    "",
    "/contact",
    "/contact-us",
    "/about",
    "/about-us",
    "/impressum"
]

BAD_EMAIL_KEYWORDS = [
    "example",
    "test",
    "noreply",
    "no-reply"
]

HEADERS = {"User-Agent": "Mozilla/5.0"}


def extract_email_from_website(base_url: str):
    emails = set()

    for path in PAGES:
        try:
            page_url = urljoin(base_url, path)
            r = requests.get(page_url, headers=HEADERS, timeout=8)

            if r.status_code != 200:
                continue

            soup = BeautifulSoup(r.text, "html.parser")

            # text emails
            text = soup.get_text(" ", strip=True)
            emails.update(EMAIL_REGEX.findall(text))

            # mailto links
            for link in soup.select('a[href^="mailto:"]'):
                email = link["href"].replace("mailto:", "").split("?")[0]
                if EMAIL_REGEX.fullmatch(email):
                    emails.add(email)

        except Exception:
            continue

    return select_best_email(emails)


def select_best_email(emails: set[str]):
    if not emails:
        return None

    clean = []
    for e in emails:
        el = e.lower()
        if any(bad in el for bad in BAD_EMAIL_KEYWORDS):
            continue

        if el.startswith(("info@", "contact@", "sales@", "office@", "hello@")):
            return e

        clean.append(e)

    return sorted(clean)[0] if clean else None


def extract_email_from_soups(soups: dict[str, BeautifulSoup]) -> str | None:
    """
    Extract best email from pre-fetched BeautifulSoup objects.
    Same logic as extract_email_from_website but without fetching.
    """
    emails = set()

    for path, soup in soups.items():
        text = soup.get_text(" ", strip=True)
        emails.update(EMAIL_REGEX.findall(text))

        for link in soup.select('a[href^="mailto:"]'):
            email = link["href"].replace("mailto:", "").split("?")[0]
            if EMAIL_REGEX.fullmatch(email):
                emails.add(email)

    return select_best_email(emails)
