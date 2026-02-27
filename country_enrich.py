"""
Country detection from multiple lightweight signals.
No extra HTTP requests -- operates on already-fetched HTML.
"""

import re
from bs4 import BeautifulSoup


# ============================================================
# Signal 1: Company name suffix -> country
# ============================================================
# Ordered from most specific to least to avoid false matches.
COMPANY_SUFFIX_MAP = [
    (r"\bPvt\.?\s*Ltd\.?\b", "India"),
    (r"\bPte\.?\s*Ltd\.?\b", "Singapore"),
    (r"\bPty\.?\s*Ltd\.?\b", "Australia"),
    (r"\bGmbH\b", "Germany"),
    (r"\bA\.?\s*[SŞ]\.?\b", "Turkey"),
    (r"\bFZCO\b", "United Arab Emirates"),
    (r"\bFZ-?LLC\b", "United Arab Emirates"),
    (r"\bFZE\b", "United Arab Emirates"),
    (r"\bB\.?\s*V\.?\b", "Netherlands"),
    (r"\bN\.?\s*V\.?\b", "Netherlands"),
    (r"\bS\.?\s*r\.?\s*l\.?\b", "Italy"),
    (r"\bS\.?\s*p\.?\s*A\.?\b", "Italy"),
    (r"\bOy\b", "Finland"),
    (r"\bAB\b", "Sweden"),
    (r"\bAG\b", "Switzerland"),
    (r"\bSARL\b", "France"),
    (r"\bS\.?\s*A\.?\s*S\.?\b", "France"),
    # Ambiguous suffixes -- return None
    (r"\bLtd\.?\b", None),
    (r"\bLLC\b", None),
    (r"\bInc\.?\b", None),
    (r"\bCorp\.?\b", None),
]


def infer_country_from_company_name(company_name: str) -> str | None:
    if not company_name:
        return None
    for pattern, country in COMPANY_SUFFIX_MAP:
        if re.search(pattern, company_name, re.IGNORECASE):
            return country
    return None


# ============================================================
# Signal 2: HTML lang attribute
# ============================================================
LANG_TO_COUNTRY = {
    "de": "Germany",
    "tr": "Turkey",
    "fr": "France",
    "it": "Italy",
    "es": "Spain",
    "pt-br": "Brazil",
    "pt-pt": "Portugal",
    "pt": "Brazil",
    "nl": "Netherlands",
    "sv": "Sweden",
    "fi": "Finland",
    "no": "Norway",
    "nb": "Norway",
    "nn": "Norway",
    "pl": "Poland",
    "cs": "Czech Republic",
    "ja": "Japan",
    "ko": "South Korea",
    "zh": "China",
    "zh-cn": "China",
    "zh-tw": "Taiwan",
    "he": "Israel",
    "iw": "Israel",
    "ru": "Russia",
    "da": "Denmark",
    "hu": "Hungary",
    "ro": "Romania",
    "el": "Greece",
    "th": "Thailand",
    "vi": "Vietnam",
    "uk": "Ukraine",
    "hi": "India",
}


def infer_country_from_html_lang(soups: list[BeautifulSoup]) -> str | None:
    for soup in soups:
        html_tag = soup.find("html")
        if html_tag and html_tag.get("lang"):
            lang = html_tag["lang"].strip().lower()
            if lang.startswith("en"):
                continue
            # Exact match first, then base language
            if lang in LANG_TO_COUNTRY:
                return LANG_TO_COUNTRY[lang]
            base = lang.split("-")[0]
            if base in LANG_TO_COUNTRY:
                return LANG_TO_COUNTRY[base]
    return None


# ============================================================
# Signal 3: Phone number country codes
# ============================================================
PHONE_REGEX = re.compile(
    r"(?<!\d)\+\s*"
    r"(\d{1,3})"
    r"[\s\-\.\(]"
)

PHONE_CODE_TO_COUNTRY = {
    "7": "Russia",
    "20": "Egypt",
    "27": "South Africa",
    "30": "Greece",
    "31": "Netherlands",
    "32": "Belgium",
    "33": "France",
    "34": "Spain",
    "36": "Hungary",
    "39": "Italy",
    "40": "Romania",
    "41": "Switzerland",
    "43": "Austria",
    "44": "United Kingdom",
    "45": "Denmark",
    "46": "Sweden",
    "47": "Norway",
    "48": "Poland",
    "49": "Germany",
    "51": "Peru",
    "52": "Mexico",
    "54": "Argentina",
    "55": "Brazil",
    "56": "Chile",
    "57": "Colombia",
    "60": "Malaysia",
    "61": "Australia",
    "62": "Indonesia",
    "63": "Philippines",
    "64": "New Zealand",
    "65": "Singapore",
    "66": "Thailand",
    "81": "Japan",
    "82": "South Korea",
    "84": "Vietnam",
    "86": "China",
    "90": "Turkey",
    "91": "India",
    "92": "Pakistan",
    "94": "Sri Lanka",
    "212": "Morocco",
    "213": "Algeria",
    "216": "Tunisia",
    "234": "Nigeria",
    "254": "Kenya",
    "351": "Portugal",
    "352": "Luxembourg",
    "353": "Ireland",
    "354": "Iceland",
    "358": "Finland",
    "370": "Lithuania",
    "371": "Latvia",
    "372": "Estonia",
    "380": "Ukraine",
    "381": "Serbia",
    "385": "Croatia",
    "386": "Slovenia",
    "420": "Czech Republic",
    "421": "Slovakia",
    "852": "Hong Kong",
    "886": "Taiwan",
    "961": "Lebanon",
    "962": "Jordan",
    "965": "Kuwait",
    "966": "Saudi Arabia",
    "968": "Oman",
    "971": "United Arab Emirates",
    "972": "Israel",
    "973": "Bahrain",
    "974": "Qatar",
}


def infer_country_from_phone_numbers(soups: list[BeautifulSoup]) -> str | None:
    country_votes: dict[str, int] = {}

    for soup in soups:
        text = soup.get_text(" ", strip=True)
        matches = PHONE_REGEX.findall(text)
        for code in matches:
            country = None
            if code[:3] in PHONE_CODE_TO_COUNTRY:
                country = PHONE_CODE_TO_COUNTRY[code[:3]]
            elif code[:2] in PHONE_CODE_TO_COUNTRY:
                country = PHONE_CODE_TO_COUNTRY[code[:2]]
            elif code[:1] in PHONE_CODE_TO_COUNTRY:
                country = PHONE_CODE_TO_COUNTRY[code[:1]]
            if country:
                country_votes[country] = country_votes.get(country, 0) + 1

    if not country_votes:
        return None
    return max(country_votes, key=country_votes.get)


# ============================================================
# Signal 4: Address / country keywords in text
# ============================================================
ADDRESS_COUNTRY_KEYWORDS = {
    "germany": "Germany",
    "deutschland": "Germany",
    "france": "France",
    "italy": "Italy",
    "italia": "Italy",
    "spain": "Spain",
    "united kingdom": "United Kingdom",
    "united arab emirates": "United Arab Emirates",
    "netherlands": "Netherlands",
    "nederland": "Netherlands",
    "switzerland": "Switzerland",
    "schweiz": "Switzerland",
    "sweden": "Sweden",
    "sverige": "Sweden",
    "norway": "Norway",
    "finland": "Finland",
    "suomi": "Finland",
    "poland": "Poland",
    "polska": "Poland",
    "czech republic": "Czech Republic",
    "turkey": "Turkey",
    "india": "India",
    "singapore": "Singapore",
    "australia": "Australia",
    "brazil": "Brazil",
    "brasil": "Brazil",
    "japan": "Japan",
    "south korea": "South Korea",
    "china": "China",
    "israel": "Israel",
    "saudi arabia": "Saudi Arabia",
    "portugal": "Portugal",
    "belgium": "Belgium",
    "austria": "Austria",
    "denmark": "Denmark",
    "ireland": "Ireland",
    "greece": "Greece",
    "russia": "Russia",
    "mexico": "Mexico",
    "canada": "Canada",
    "south africa": "South Africa",
    "new zealand": "New Zealand",
    "malaysia": "Malaysia",
    "thailand": "Thailand",
    "vietnam": "Vietnam",
    "indonesia": "Indonesia",
    "philippines": "Philippines",
    "taiwan": "Taiwan",
    "hong kong": "Hong Kong",
    "dubai": "United Arab Emirates",
    "abu dhabi": "United Arab Emirates",
}


def infer_country_from_address_text(soups: list[BeautifulSoup]) -> str | None:
    country_votes: dict[str, int] = {}

    for soup in soups:
        # Prioritize structured address-like elements
        candidates = soup.find_all(["footer", "address"])
        for el in soup.find_all(["div", "section", "p"], limit=200):
            el_id = (el.get("id") or "").lower()
            el_class = " ".join(el.get("class") or []).lower()
            if any(kw in el_id or kw in el_class
                   for kw in ("contact", "address", "footer", "location", "impressum")):
                candidates.append(el)

        texts = []
        if candidates:
            texts = [el.get_text(" ", strip=True).lower() for el in candidates]
        else:
            texts = [soup.get_text(" ", strip=True).lower()]

        for text in texts:
            for keyword, country in ADDRESS_COUNTRY_KEYWORDS.items():
                if keyword in text:
                    country_votes[country] = country_votes.get(country, 0) + 1

    if not country_votes:
        return None
    return max(country_votes, key=country_votes.get)


# ============================================================
# Resolver: combine all signals
# ============================================================
CONFIDENCE_HIGH = "high"
CONFIDENCE_MEDIUM = "medium"
CONFIDENCE_LOW = "low"


def resolve_country(
    cctld_country: str | None,
    suffix_country: str | None,
    lang_country: str | None,
    phone_country: str | None,
    address_country: str | None,
) -> tuple[str | None, str]:
    """
    Combine all signals into a single best-guess country.

    ccTLD wins outright. Otherwise majority vote with weights.
    Returns (country_name, confidence).
    """
    if cctld_country:
        return (cctld_country, CONFIDENCE_HIGH)

    signals = []
    if suffix_country:
        signals.append((suffix_country, 3))
    if lang_country:
        signals.append((lang_country, 2))
    if phone_country:
        signals.append((phone_country, 2))
    if address_country:
        signals.append((address_country, 1))

    if not signals:
        return (None, CONFIDENCE_LOW)

    votes: dict[str, int] = {}
    weights: dict[str, int] = {}
    for country, weight in signals:
        votes[country] = votes.get(country, 0) + 1
        weights[country] = weights.get(country, 0) + weight

    winner = max(votes, key=lambda c: (votes[c], weights[c]))

    if votes[winner] >= 2:
        return (winner, CONFIDENCE_HIGH)

    if winner == address_country and len(signals) == 1:
        return (winner, CONFIDENCE_LOW)

    return (winner, CONFIDENCE_MEDIUM)


def detect_country(
    company_name: str,
    website: str,
    cctld_country: str | None,
    soups: list[BeautifulSoup],
) -> tuple[str | None, str]:
    """
    Main entry point. Runs all signal extractors and resolves.
    Returns (country_name, confidence).
    """
    suffix_country = infer_country_from_company_name(company_name)
    lang_country = infer_country_from_html_lang(soups)
    phone_country = infer_country_from_phone_numbers(soups)
    address_country = infer_country_from_address_text(soups)

    return resolve_country(
        cctld_country=cctld_country,
        suffix_country=suffix_country,
        lang_country=lang_country,
        phone_country=phone_country,
        address_country=address_country,
    )
