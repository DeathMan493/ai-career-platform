from __future__ import annotations

from datetime import datetime, timezone

from app.ingestion.mongo import get_database
from app.schemas.auth import AuthPayload, AuthUser
from app.schemas.profile import ProfilePayload, SkillItem, UpdateProfileRequest
from app.services.graph_projection_service import sync_user_graph_if_available
from app.services.progress_service import build_effective_profile, recalculate_and_persist_progress


DEFAULT_CAREER_GOAL = "AI Researcher"


def _users_collection():
    return get_database()["users"]


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _profile_from_document(document: dict) -> ProfilePayload:
    skills = [SkillItem(**item) for item in (document.get("skills") or [])]
    return ProfilePayload(
        id=document["firebase_uid"],
        name=document.get("name") or document.get("email", "User"),
        career_goal=document.get("career_goal") or DEFAULT_CAREER_GOAL,
        skills=skills,
    )


def get_or_create_user_from_firebase(decoded_token: dict) -> AuthPayload:
    collection = _users_collection()
    firebase_uid = decoded_token["uid"]
    email = decoded_token.get("email", "")
    name = decoded_token.get("name") or decoded_token.get("display_name") or email.split("@")[0] or "User"
    now = _utc_now()
    existing_document = collection.find_one({"firebase_uid": firebase_uid})

    if existing_document:
        set_fields = {
            "email": email,
            "name": name,
            "last_login_at": now,
            "updated_at": now,
        }

        # Backfill required fields for users created before schema validation was added.
        if "career_goal" not in existing_document:
            set_fields["career_goal"] = DEFAULT_CAREER_GOAL
        if "skills" not in existing_document:
            set_fields["skills"] = []
        if "completed_courses" not in existing_document:
            set_fields["completed_courses"] = []
        if "completed_papers" not in existing_document:
            set_fields["completed_papers"] = []
        if "derived_skills" not in existing_document:
            set_fields["derived_skills"] = []
        if "skill_progress" not in existing_document:
            set_fields["skill_progress"] = []
        if "created_at" not in existing_document:
            set_fields["created_at"] = now

        collection.update_one({"firebase_uid": firebase_uid}, {"$set": set_fields}, upsert=False)
    else:
        collection.insert_one(
            {
                "firebase_uid": firebase_uid,
                "email": email,
                "name": name,
                "career_goal": DEFAULT_CAREER_GOAL,
                "skills": [],
                "completed_courses": [],
                "completed_papers": [],
                "derived_skills": [],
                "skill_progress": [],
                "created_at": now,
                "updated_at": now,
                "last_login_at": now,
            }
        )

    recalculate_and_persist_progress(firebase_uid)
    sync_user_graph_if_available(firebase_uid)

    return AuthPayload(
        user=AuthUser(id=firebase_uid, name=name, email=email),
        token=decoded_token.get("uid", firebase_uid),
    )


def get_profile_by_uid(firebase_uid: str) -> ProfilePayload:
    collection = _users_collection()
    document = collection.find_one({"firebase_uid": firebase_uid})
    if not document:
        raise ValueError("User profile not found")
    return _profile_from_document(document)


def get_effective_profile_by_uid(firebase_uid: str) -> ProfilePayload:
    collection = _users_collection()
    document = collection.find_one({"firebase_uid": firebase_uid})
    if not document:
        raise ValueError("User profile not found")
    return build_effective_profile(document)


def update_profile_by_uid(firebase_uid: str, payload: UpdateProfileRequest) -> ProfilePayload:
    collection = _users_collection()
    collection.update_one(
        {"firebase_uid": firebase_uid},
        {
            "$set": {
                "career_goal": payload.career_goal,
                "skills": [item.model_dump() for item in payload.skills],
                "updated_at": _utc_now(),
            }
        },
        upsert=False,
    )
    document = collection.find_one({"firebase_uid": firebase_uid})
    if not document:
        raise ValueError("User profile not found after update")
    recalculate_and_persist_progress(firebase_uid)
    sync_user_graph_if_available(firebase_uid)
    return _profile_from_document(document)
