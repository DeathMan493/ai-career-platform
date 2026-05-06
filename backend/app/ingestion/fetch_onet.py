from __future__ import annotations

import argparse
from pprint import pprint

import httpx

from app.core.config import settings


DEFAULT_ENDPOINT = "online/occupations/"


def fetch_onet_placeholder(endpoint: str) -> dict:
    if not settings.onet_api_key:
        raise ValueError("ONET_API_KEY must be set in backend/.env before using O*NET.")

    base_url = settings.onet_base_url.rstrip("/")
    normalized_endpoint = endpoint.lstrip("/")
    headers = {
        "X-API-Key": settings.onet_api_key,
        "Accept": "application/json",
    }

    with httpx.Client(base_url=f"{base_url}/", timeout=30.0, headers=headers) as client:
        response = client.get(normalized_endpoint)
        response.raise_for_status()
        return response.json()


def main() -> None:
    parser = argparse.ArgumentParser(description="Starter O*NET fetch placeholder for later ingestion work.")
    parser.add_argument(
        "--endpoint",
        default=DEFAULT_ENDPOINT,
        help="Relative O*NET endpoint, for example 'online/occupations/' or 'online/occupations/15-1252.00/'.",
    )
    args = parser.parse_args()

    payload = fetch_onet_placeholder(args.endpoint)
    pprint(payload)


if __name__ == "__main__":
    main()
