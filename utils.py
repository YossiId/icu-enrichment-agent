import tldextract

CC_TLD_MAP = {
    "il": "Israel",
    "tr": "Turkey",
    "de": "Germany",
    "fr": "France",
    "it": "Italy",
    "es": "Spain",
    "uk": "United Kingdom",
    "ae": "United Arab Emirates",
    "sa": "Saudi Arabia",
    "nl": "Netherlands",
    "ch": "Switzerland",
    "se": "Sweden",
    "no": "Norway",
    "fi": "Finland",
    "pl": "Poland",
    "cz": "Czech Republic",
    "jp": "Japan",
    "kr": "South Korea",
    "cn": "China",
    "in": "India",
    "au": "Australia",
    "br": "Brazil",
    "mx": "Mexico",
    # New additions
    "at": "Austria",
    "be": "Belgium",
    "dk": "Denmark",
    "ie": "Ireland",
    "pt": "Portugal",
    "gr": "Greece",
    "hu": "Hungary",
    "ro": "Romania",
    "ru": "Russia",
    "za": "South Africa",
    "sg": "Singapore",
    "my": "Malaysia",
    "th": "Thailand",
    "id": "Indonesia",
    "ph": "Philippines",
    "vn": "Vietnam",
    "tw": "Taiwan",
    "hk": "Hong Kong",
    "nz": "New Zealand",
    "ar": "Argentina",
    "cl": "Chile",
    "pe": "Peru",
    "eg": "Egypt",
    "ng": "Nigeria",
    "ke": "Kenya",
}

AMBIGUOUS_TLDS = {"io", "ai", "me", "tv", "co"}


def infer_country_from_domain(website: str) -> str | None:
    """
    Infer country from domain ccTLD using tldextract.
    Returns country name or None if uncertain.
    """
    try:
        extracted = tldextract.extract(website)
        suffix = extracted.suffix.lower()
        # Handle compound TLDs like "co.uk" -> last part is "uk"
        tld = suffix.split(".")[-1]

        if tld in CC_TLD_MAP:
            return CC_TLD_MAP[tld]

        if tld in AMBIGUOUS_TLDS:
            return None

        return None
    except Exception:
        return None
