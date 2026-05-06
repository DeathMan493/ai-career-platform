from __future__ import annotations

import argparse
import csv
from pathlib import Path

from pymongo import UpdateOne

from app.core.config import settings
from app.ingestion.mongo import get_database
from app.ingestion.normalizers import normalize_course_document


BACKEND_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_DIR.parent
DATA_ROOT = PROJECT_ROOT / settings.data_dir
DEFAULT_FILES = [
    DATA_ROOT / "coursera course and skill 2024" / "coursera_course_dataset_v2_no_null.csv",
    DATA_ROOT / "coursera course and skill 2024" / "coursera_course_dataset_v3.csv",
    DATA_ROOT / "edx Udacity courera" / "final_cleaned_dataset.csv",
]


def resolve_csv_path(path_value: str | Path) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path

    project_relative = PROJECT_ROOT / path
    if project_relative.exists():
        return project_relative

    backend_relative = BACKEND_DIR / path
    return backend_relative


def iter_rows(csv_path: Path):
    with csv_path.open("r", encoding="utf-8-sig", newline="") as file_handle:
        reader = csv.DictReader(file_handle)
        for row in reader:
            yield row


def import_courses(csv_paths: list[Path], collection_name: str, dry_run: bool) -> None:
    database = get_database()
    collection = database[collection_name]
    operations: list[UpdateOne] = []
    total = 0

    for csv_path in csv_paths:
        resolved_path = resolve_csv_path(csv_path)
        if not resolved_path.exists():
            raise FileNotFoundError(f"Course dataset not found: {resolved_path}")

        source = resolved_path.parent.name
        for row in iter_rows(resolved_path):
            document = normalize_course_document(row, source=source)
            if not document["title"]:
                continue

            total += 1
            operations.append(
                UpdateOne(
                    {"source": document["source"], "source_id": document["source_id"], "title": document["title"]},
                    {"$set": document},
                    upsert=True,
                )
            )

    print(f"Prepared {total} course documents for collection '{collection_name}'.")

    if dry_run:
        print("Dry run enabled. No MongoDB writes were performed.")
        return

    if operations:
        result = collection.bulk_write(operations, ordered=False)
        collection.create_index([("title", 1)])
        collection.create_index([("provider", 1)])
        collection.create_index([("skills", 1)])
        print(
            "MongoDB write complete:",
            {
                "upserted": result.upserted_count,
                "modified": result.modified_count,
                "matched": result.matched_count,
            },
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Import normalized course datasets into MongoDB.")
    parser.add_argument("--collection", default="courses", help="MongoDB collection name.")
    parser.add_argument("--dry-run", action="store_true", help="Parse and normalize without writing to MongoDB.")
    parser.add_argument("files", nargs="*", help="Optional CSV file paths. Defaults to the known downloaded datasets.")
    args = parser.parse_args()

    csv_paths = [resolve_csv_path(path) for path in args.files] if args.files else DEFAULT_FILES
    import_courses(csv_paths=csv_paths, collection_name=args.collection, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
