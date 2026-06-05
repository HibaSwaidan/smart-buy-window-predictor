# src/services/asin_parser.py

import re


ASIN_REGEX = re.compile(r"^[A-Z0-9]{10}$")

AMAZON_URL_PATTERNS = [
    re.compile(r"/dp/([A-Z0-9]{10})"),
    re.compile(r"/gp/product/([A-Z0-9]{10})"),
    re.compile(r"/product/([A-Z0-9]{10})"),
    re.compile(r"/ASIN/([A-Z0-9]{10})"),
]


def extract_asin(url_or_asin: str) -> str:
    """
    Extract an Amazon ASIN from either a raw ASIN or an Amazon product URL.
    """

    if not url_or_asin or not isinstance(url_or_asin, str):
        raise ValueError("Input must be a non-empty Amazon URL or ASIN.")

    value = url_or_asin.strip()

    # Raw ASIN
    if ASIN_REGEX.fullmatch(value):
        return value

    # Amazon URL patterns
    for pattern in AMAZON_URL_PATTERNS:
        match = pattern.search(value)
        if match:
            return match.group(1)

    # Fallback: search any 10-character ASIN-like token in the URL
    fallback_match = re.search(r"([A-Z0-9]{10})", value)
    if fallback_match:
        return fallback_match.group(1)

    raise ValueError("Could not extract a valid ASIN from the provided input.")