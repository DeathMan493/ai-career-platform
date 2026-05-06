from __future__ import annotations

import re
from typing import Any


SKILL_SPLIT_PATTERN = re.compile(r"\s*[,/|]\s*|\s+and\s+", re.IGNORECASE)
NUMBER_PATTERN = re.compile(r"[^0-9.]+")


def parse_skills(value: str | None) -> list[str]:
    if not value:
        return []

    parts = [part.strip() for part in SKILL_SPLIT_PATTERN.split(value) if part.strip()]
    deduped: list[str] = []
    seen: set[str] = set()

    for part in parts:
        normalized = part.casefold()
        if normalized not in seen:
            seen.add(normalized)
            deduped.append(part)

    return deduped


def parse_float(value: Any) -> float | None:
    if value in (None, ""):
        return None

    if isinstance(value, (int, float)):
        return float(value)

    cleaned = NUMBER_PATTERN.sub("", str(value))
    if not cleaned:
        return None

    try:
        return float(cleaned)
    except ValueError:
        return None


def parse_int(value: Any) -> int | None:
    number = parse_float(value)
    if number is None:
        return None
    return int(number)


def compact_text(value: Any) -> str | None:
    if value in (None, ""):
        return None

    text = str(value).strip()
    return text or None


def normalize_course_document(raw: dict[str, Any], source: str) -> dict[str, Any]:
    title = compact_text(raw.get("Title") or raw.get("Course_Name"))
    provider = compact_text(raw.get("Organization") or raw.get("Platform"))
    skills = parse_skills(raw.get("Skills"))
    rating = parse_float(raw.get("Ratings") or raw.get("Rating"))
    review_count = parse_int(raw.get("Review counts") or raw.get("Review Count"))
    enrolled = compact_text(raw.get("course_students_enrolled") or raw.get("Number of students"))
    difficulty = compact_text(raw.get("Difficulty") or raw.get("Level"))
    course_type = compact_text(raw.get("Type"))
    duration = compact_text(raw.get("Duration"))
    description = compact_text(raw.get("course_description") or raw.get("Metadata"))
    source_url = compact_text(raw.get("course_url"))
    source_id = compact_text(raw.get("") or raw.get("id") or title)

    return {
        "source": source,
        "source_id": source_id,
        "title": title,
        "provider": provider,
        "skills": skills,
        "rating": rating,
        "review_count": review_count,
        "students_enrolled": enrolled,
        "difficulty": difficulty,
        "course_type": course_type,
        "duration": duration,
        "description": description,
        "url": source_url,
        "raw": raw,
    }


def normalize_openalex_work(raw: dict[str, Any]) -> dict[str, Any]:
    authorships = raw.get("authorships") or []
    concepts = raw.get("concepts") or []

    return {
        "source": "openalex",
        "source_id": raw.get("id"),
        "title": compact_text(raw.get("title")),
        "abstract": compact_text(raw.get("abstract_inverted_index")) or compact_text(raw.get("abstract")),
        "publication_year": raw.get("publication_year"),
        "doi": compact_text(raw.get("doi")),
        "openalex_id": compact_text(raw.get("id")),
        "primary_location": raw.get("primary_location"),
        "authors": [
            compact_text(authorship.get("author", {}).get("display_name"))
            for authorship in authorships
            if compact_text(authorship.get("author", {}).get("display_name"))
        ],
        "concepts": [
            {
                "name": concept.get("display_name"),
                "score": concept.get("score"),
            }
            for concept in concepts
            if concept.get("display_name")
        ],
        "keywords": [concept.get("display_name") for concept in concepts if concept.get("display_name")],
        "url": compact_text((raw.get("primary_location") or {}).get("landing_page_url")),
        "raw": raw,
    }


def normalize_usajobs_position(raw: dict[str, Any]) -> dict[str, Any]:
    descriptor = raw.get("MatchedObjectDescriptor", {})
    locations = descriptor.get("PositionLocation", []) or []
    details = descriptor.get("UserArea", {}).get("Details", {})
    remuneration = descriptor.get("PositionRemuneration", []) or []

    return {
        "source": "usajobs",
        "source_id": compact_text(descriptor.get("PositionID")),
        "title": compact_text(descriptor.get("PositionTitle")),
        "organization": compact_text(descriptor.get("OrganizationName")),
        "department": compact_text(descriptor.get("DepartmentName")),
        "locations": [location.get("LocationName") for location in locations if location.get("LocationName")],
        "minimum_salary": (remuneration[0] or {}).get("MinimumRange") if remuneration else None,
        "maximum_salary": (remuneration[0] or {}).get("MaximumRange") if remuneration else None,
        "qualification_summary": compact_text(details.get("MajorDuties") or details.get("QualificationSummary")),
        "requirements": compact_text(details.get("Education") or details.get("Requirements")),
        "security_clearance": compact_text(details.get("SecurityClearance")),
        "travel_required": compact_text(details.get("TravelRequired")),
        "apply_url": compact_text(descriptor.get("PositionURI")),
        "raw": raw,
    }
