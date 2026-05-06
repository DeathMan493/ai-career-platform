from __future__ import annotations

from datetime import datetime, timezone

from app.ingestion.mongo import get_database
from app.schemas.dashboard import CourseItem, PaperItem
from app.schemas.profile import ProfilePayload, SkillItem
from app.schemas.progress import (
    CompletedCourseItem,
    CompletedPaperItem,
    DerivedSkillItem,
    SkillProgressItem,
    UserProgressPayload,
)


LEVEL_PROGRESS = {
    "Beginner": 35,
    "Intermediate": 60,
    "Advanced": 85,
}
COURSE_SKILL_BOOST = 22
PAPER_SKILL_BOOST = 14
AUTO_ADD_THRESHOLD = 25


def _users_collection():
    return get_database()["users"]


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _utc_now_iso() -> str:
    return _utc_now().isoformat()


def _normalize_skill_name(value: str | None) -> str:
    return (value or "").strip()


def _progress_to_level(progress: int) -> str:
    if progress >= 80:
        return "Advanced"
    if progress >= 55:
        return "Intermediate"
    return "Beginner"


def _build_completed_skill_boosts(document: dict) -> dict[str, int]:
    progress_map: dict[str, int] = {}

    for course in document.get("completed_courses") or []:
        for tag in course.get("tags") or []:
            skill = _normalize_skill_name(tag)
            if not skill:
                continue
            progress_map[skill] = min(100, progress_map.get(skill, 0) + COURSE_SKILL_BOOST)

    for paper in document.get("completed_papers") or []:
        for tag in paper.get("tags") or []:
            skill = _normalize_skill_name(tag)
            if not skill:
                continue
            progress_map[skill] = min(100, progress_map.get(skill, 0) + PAPER_SKILL_BOOST)

    return progress_map


def derive_skill_state_from_document(document: dict) -> tuple[list[dict], list[dict], list[dict]]:
    manual_skills = list(document.get("skills") or [])
    progress_map = _build_completed_skill_boosts(document)
    manual_skill_names: set[str] = set()

    normalized_manual_skills: list[dict] = []
    for item in manual_skills:
        skill = _normalize_skill_name(item.get("skill"))
        if not skill:
            continue

        manual_skill_names.add(skill)
        base_progress = LEVEL_PROGRESS.get(item.get("level"), LEVEL_PROGRESS["Beginner"])
        completion_boost = progress_map.get(skill, 0)
        total_progress = min(100, max(base_progress, completion_boost))
        progress_map[skill] = total_progress

        normalized_manual_skills.append({
            "skill": skill,
            "level": _progress_to_level(total_progress),
        })

    derived_skills: list[dict] = []
    for skill, progress in sorted(progress_map.items(), key=lambda entry: entry[0]):
        if skill in manual_skill_names or progress < AUTO_ADD_THRESHOLD:
            continue
        derived_skills.append({
            "skill": skill,
            "level": _progress_to_level(progress),
            "progress": progress,
        })

    skill_progress = [
        {
            "skill": skill,
            "progress": progress,
        }
        for skill, progress in sorted(progress_map.items(), key=lambda entry: entry[0])
    ]

    return normalized_manual_skills, derived_skills, skill_progress


def _effective_skills_from_document(document: dict) -> list[SkillItem]:
    manual_skills, derived_skills, _skill_progress = derive_skill_state_from_document(document)
    merged = manual_skills + [
        {
            "skill": item["skill"],
            "level": item["level"],
        }
        for item in derived_skills
    ]
    return [SkillItem(**item) for item in merged]


def build_effective_profile(document: dict) -> ProfilePayload:
    return ProfilePayload(
        id=document["firebase_uid"],
        name=document.get("name") or document.get("email", "User"),
        career_goal=document.get("career_goal") or "AI Researcher",
        skills=_effective_skills_from_document(document),
    )


def recalculate_and_persist_progress(firebase_uid: str) -> UserProgressPayload:
    from app.services.graph_projection_service import sync_user_graph_if_available

    collection = _users_collection()
    document = collection.find_one({"firebase_uid": firebase_uid})
    if not document:
        raise ValueError("User progress not found")

    _manual_skills, derived_skills, skill_progress = derive_skill_state_from_document(document)

    collection.update_one(
        {"firebase_uid": firebase_uid},
        {
            "$set": {
                "derived_skills": derived_skills,
                "skill_progress": skill_progress,
                "updated_at": _utc_now(),
            }
        },
    )

    refreshed = collection.find_one({"firebase_uid": firebase_uid})
    sync_user_graph_if_available(firebase_uid)
    return _progress_payload_from_document(refreshed)


def _progress_payload_from_document(document: dict) -> UserProgressPayload:
    completed_courses = [CompletedCourseItem(**item) for item in (document.get("completed_courses") or [])]
    completed_papers = [CompletedPaperItem(**item) for item in (document.get("completed_papers") or [])]
    derived_skills = [DerivedSkillItem(**item) for item in (document.get("derived_skills") or [])]
    skill_progress = [SkillProgressItem(**item) for item in (document.get("skill_progress") or [])]
    return UserProgressPayload(
        completed_courses=completed_courses,
        completed_papers=completed_papers,
        derived_skills=derived_skills,
        skill_progress=skill_progress,
    )


def get_progress_by_uid(firebase_uid: str) -> UserProgressPayload:
    collection = _users_collection()
    document = collection.find_one({"firebase_uid": firebase_uid})
    if not document:
        raise ValueError("User progress not found")
    if "derived_skills" not in document or "skill_progress" not in document:
        return recalculate_and_persist_progress(firebase_uid)
    return _progress_payload_from_document(document)


def _add_completed_item(firebase_uid: str, field_name: str, item_payload: dict) -> UserProgressPayload:
    collection = _users_collection()
    document = collection.find_one({"firebase_uid": firebase_uid})
    if not document:
        raise ValueError("User not found for completion update")

    current_items = list(document.get(field_name) or [])
    if not any(item.get("id") == item_payload["id"] for item in current_items):
        current_items.append({
            **item_payload,
            "completed_at": _utc_now_iso(),
        })
        collection.update_one(
            {"firebase_uid": firebase_uid},
            {
                "$set": {
                    field_name: current_items,
                    "updated_at": _utc_now(),
                }
            },
        )

    return recalculate_and_persist_progress(firebase_uid)


def _remove_completed_item(firebase_uid: str, field_name: str, item_id: str) -> UserProgressPayload:
    collection = _users_collection()
    collection.update_one(
        {"firebase_uid": firebase_uid},
        {
            "$pull": {
                field_name: {"id": item_id}
            },
            "$set": {
                "updated_at": _utc_now(),
            }
        },
    )
    return recalculate_and_persist_progress(firebase_uid)


def complete_course_by_uid(firebase_uid: str, payload: CourseItem) -> UserProgressPayload:
    return _add_completed_item(firebase_uid, "completed_courses", payload.model_dump())


def uncomplete_course_by_uid(firebase_uid: str, item_id: str) -> UserProgressPayload:
    return _remove_completed_item(firebase_uid, "completed_courses", item_id)


def complete_paper_by_uid(firebase_uid: str, payload: PaperItem) -> UserProgressPayload:
    return _add_completed_item(firebase_uid, "completed_papers", payload.model_dump())


def uncomplete_paper_by_uid(firebase_uid: str, item_id: str) -> UserProgressPayload:
    return _remove_completed_item(firebase_uid, "completed_papers", item_id)
