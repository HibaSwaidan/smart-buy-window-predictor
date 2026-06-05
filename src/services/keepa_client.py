# src/services/keepa_client.py

import os
from typing import Any, Dict

import keepa
from dotenv import load_dotenv


load_dotenv()


def get_keepa_api() -> keepa.Keepa:
    """
    Create a Keepa API client using the API key from .env.
    """

    api_key = os.getenv("KEEPA_API_KEY")

    if not api_key:
        raise ValueError("Missing KEEPA_API_KEY. Add it to your local .env file or deployment environment variables.")

    return keepa.Keepa(api_key)


def fetch_keepa_product(asin: str, domain: str = "US") -> Dict[str, Any]:
    """
    Fetch one product from Keepa.

    Important:
    The current MVP model was trained without Buy Box features.
    Therefore, this function uses history=True only and does not request buybox=True or offers=20.
    """

    api = get_keepa_api()

    products = api.query(
        [asin],
        domain=domain,
        history=True
    )

    if not products:
        raise ValueError(f"No product data returned from Keepa for ASIN: {asin}")

    product = products[0]

    if not product or not product.get("asin"):
        raise ValueError(f"Invalid product data returned from Keepa for ASIN: {asin}")

    return product