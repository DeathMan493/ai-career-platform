from __future__ import annotations

import logging

from pymongo.errors import CollectionInvalid, OperationFailure, PyMongoError

from app.ingestion.mongo import get_database

logger = logging.getLogger(__name__)


USER_COLLECTION_VALIDATOR = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            "firebase_uid",
            "email",
            "name",
            "career_goal",
            "skills",
            "completed_courses",
            "completed_papers",
            "derived_skills",
            "skill_progress",
        ],
        "properties": {
            "firebase_uid": {
                "bsonType": "string",
                "description": "Firebase user id must be stored as a string.",
            },
            "email": {
                "bsonType": "string",
                "description": "User email must be stored as a string.",
            },
            "name": {
                "bsonType": "string",
                "description": "Display name must be stored as a string.",
            },
            "career_goal": {
                "bsonType": "string",
                "description": "Career goal must be stored as a string.",
            },
            "skills": {
                "bsonType": "array",
                "items": {
                    "bsonType": "object",
                    "required": ["skill", "level"],
                    "properties": {
                        "skill": {"bsonType": "string"},
                        "level": {"bsonType": "string"},
                    },
                },
            },
            "completed_courses": {
                "bsonType": "array",
                "items": {
                    "bsonType": "object",
                    "required": ["id", "title", "reason", "tags", "provider", "level", "duration", "completed_at"],
                    "properties": {
                        "id": {"bsonType": "string"},
                        "title": {"bsonType": "string"},
                        "reason": {"bsonType": "string"},
                        "tags": {
                            "bsonType": "array",
                            "items": {"bsonType": "string"},
                        },
                        "provider": {"bsonType": "string"},
                        "level": {"bsonType": "string"},
                        "duration": {"bsonType": "string"},
                        "completed_at": {"bsonType": "string"},
                    },
                },
            },
            "completed_papers": {
                "bsonType": "array",
                "items": {
                    "bsonType": "object",
                    "required": ["id", "title", "reason", "tags", "venue", "year", "completed_at"],
                    "properties": {
                        "id": {"bsonType": "string"},
                        "title": {"bsonType": "string"},
                        "reason": {"bsonType": "string"},
                        "tags": {
                            "bsonType": "array",
                            "items": {"bsonType": "string"},
                        },
                        "venue": {"bsonType": "string"},
                        "year": {"bsonType": "int"},
                        "completed_at": {"bsonType": "string"},
                    },
                },
            },
            "derived_skills": {
                "bsonType": "array",
                "items": {
                    "bsonType": "object",
                    "required": ["skill", "level", "progress"],
                    "properties": {
                        "skill": {"bsonType": "string"},
                        "level": {"bsonType": "string"},
                        "progress": {"bsonType": "int"},
                    },
                },
            },
            "skill_progress": {
                "bsonType": "array",
                "items": {
                    "bsonType": "object",
                    "required": ["skill", "progress"],
                    "properties": {
                        "skill": {"bsonType": "string"},
                        "progress": {"bsonType": "int"},
                    },
                },
            },
            "created_at": {"bsonType": ["date", "null"]},
            "updated_at": {"bsonType": ["date", "null"]},
            "last_login_at": {"bsonType": ["date", "null"]},
        },
    }
}


def ensure_users_collection_validator() -> None:
    database = get_database()

    try:
        database.create_collection(
            "users",
            validator=USER_COLLECTION_VALIDATOR,
            validationLevel="strict",
            validationAction="error",
        )
        logger.info("Created MongoDB users collection with JSON schema validator.")
        return
    except CollectionInvalid:
        pass

    try:
        database.command(
            "collMod",
            "users",
            validator=USER_COLLECTION_VALIDATOR,
            validationLevel="strict",
            validationAction="error",
        )
        logger.info("Updated MongoDB users collection validator.")
    except OperationFailure as exc:
        logger.warning("Could not apply MongoDB users collection validator: %s", exc)


def ensure_database_guards() -> None:
    try:
        ensure_users_collection_validator()
    except PyMongoError:
        logger.warning("MongoDB startup validation skipped because the database is unavailable.")
