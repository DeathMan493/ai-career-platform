from __future__ import annotations

import argparse

import httpx
from pymongo import UpdateOne

from app.core.config import settings
from app.ingestion.mongo import get_database
from app.ingestion.normalizers import normalize_usajobs_position


DEFAULT_KEYWORD = "artificial intelligence"


def fetch_usajobs_positions(keyword: str, results_per_page: int, page: int) -> list[dict]:
    headers = {
        "Host": settings.usajobs_host,
        "User-Agent": settings.usajobs_user_agent or "",
        "Authorization-Key": settings.usajobs_api_key or "",
    }
    params = {
        "Keyword": keyword,
        "ResultsPerPage": results_per_page,
        "Page": page,
    }

    with httpx.Client(base_url="https://data.usajobs.gov", timeout=30.0, headers=headers) as client:
        response = client.get("/api/search", params=params)
        response.raise_for_status()
        payload = response.json()

    return payload.get("SearchResult", {}).get("SearchResultItems", [])


def import_usajobs(keyword: str, results_per_page: int, page: int, collection_name: str, dry_run: bool) -> None:
    positions = fetch_usajobs_positions(keyword=keyword, results_per_page=results_per_page, page=page)
    print(f"Fetched {len(positions)} USAJOBS positions for keyword '{keyword}'.")

    if dry_run:
        return

    database = get_database()
    collection = database[collection_name]
    operations: list[UpdateOne] = []

    for position in positions:
        document = normalize_usajobs_position(position)
        if not document["title"]:
            continue

        operations.append(
            UpdateOne(
                {"source": document["source"], "source_id": document["source_id"]},
                {"$set": document},
                upsert=True,
            )
        )

    if operations:
        result = collection.bulk_write(operations, ordered=False)
        collection.create_index([("title", 1)])
        collection.create_index([("organization", 1)])
        collection.create_index([("locations", 1)])
        print(
            "MongoDB write complete:",
            {
                "upserted": result.upserted_count,
                "modified": result.modified_count,
                "matched": result.matched_count,
            },
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch USAJOBS listings and upsert them into MongoDB.")
    parser.add_argument("--keyword", default=DEFAULT_KEYWORD, help="Search keyword for USAJOBS.")
    parser.add_argument("--results-per-page", type=int, default=25, help="How many records to fetch per page.")
    parser.add_argument("--page", type=int, default=1, help="Pagination page number.")
    parser.add_argument("--collection", default="jobs", help="MongoDB collection name.")
    parser.add_argument("--dry-run", action="store_true", help="Fetch and print summary without writing to MongoDB.")
    args = parser.parse_args()

    import_usajobs(
        keyword=args.keyword,
        results_per_page=args.results_per_page,
        page=args.page,
        collection_name=args.collection,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
