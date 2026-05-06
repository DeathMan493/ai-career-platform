from __future__ import annotations

import re

from app.ingestion.mongo import get_database


def _skills_collection():
    return get_database()["skills"]


def _unique_skill_names(documents: list[dict]) -> list[str]:
    seen: set[str] = set()
    names: list[str] = []

    for document in documents:
        name = (document.get("name") or "").strip()
        if not name or name in seen:
            continue
        seen.add(name)
        names.append(name)

    return names


def get_skill_suggestions(q: str, limit: int = 8) -> list[str]:
    collection = _skills_collection()
    query = q.strip()

    if not query:
        documents = list(
            collection.find({}, {"name": 1})
            .sort([("occurrence_count", -1), ("name", 1)])
            .limit(limit)
        )
        return _unique_skill_names(documents)

    escaped = re.escape(query)
    prefix_matches = list(
        collection.find({"name": {"$regex": f"^{escaped}", "$options": "i"}}, {"name": 1})
        .sort([("occurrence_count", -1), ("name", 1)])
        .limit(limit)
    )

    names = _unique_skill_names(prefix_matches)
    if len(names) >= limit:
        return names[:limit]

    contains_matches = list(
        collection.find({"name": {"$regex": escaped, "$options": "i"}}, {"name": 1})
        .sort([("occurrence_count", -1), ("name", 1)])
        .limit(limit * 2)
    )

    for name in _unique_skill_names(contains_matches):
        if name not in names:
            names.append(name)
        if len(names) >= limit:
            break

    return names[:limit]
