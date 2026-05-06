from __future__ import annotations

import argparse

import httpx
from pymongo import UpdateOne

from app.core.config import settings
from app.ingestion.mongo import get_database
from app.ingestion.normalizers import normalize_openalex_work


DEFAULT_QUERY = "artificial intelligence"


def fetch_openalex_works(query: str, per_page: int, page: int) -> list[dict]:
    headers = {}
    params = {
        "search": query,
        "per-page": per_page,
        "page": page,
    }

    if settings.openalex_api_key:
        params["api_key"] = settings.openalex_api_key

    with httpx.Client(base_url=settings.openalex_base_url, timeout=30.0, headers=headers) as client:
        response = client.get("/works", params=params)
        response.raise_for_status()
        payload = response.json()

    return payload.get("results", [])


def import_openalex(query: str, per_page: int, page: int, collection_name: str, dry_run: bool) -> None:
    works = fetch_openalex_works(query=query, per_page=per_page, page=page)
    print(f"Fetched {len(works)} OpenAlex works for query '{query}'.")

    if dry_run:
        return

    database = get_database()
    collection = database[collection_name]
    operations: list[UpdateOne] = []

    for work in works:
        document = normalize_openalex_work(work)
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
        collection.create_index([("keywords", 1)])
        collection.create_index([("publication_year", -1)])
        print(
            "MongoDB write complete:",
            {
                "upserted": result.upserted_count,
                "modified": result.modified_count,
                "matched": result.matched_count,
            },
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch OpenAlex works and upsert them into MongoDB.")
    parser.add_argument("--query", default=DEFAULT_QUERY, help="Search query for OpenAlex works.")
    parser.add_argument("--per-page", type=int, default=25, help="How many records to fetch per page.")
    parser.add_argument("--page", type=int, default=1, help="Pagination page number.")
    parser.add_argument("--collection", default="papers", help="MongoDB collection name.")
    parser.add_argument("--dry-run", action="store_true", help="Fetch and print summary without writing to MongoDB.")
    args = parser.parse_args()

    import_openalex(
        query=args.query,
        per_page=args.per_page,
        page=args.page,
        collection_name=args.collection,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
