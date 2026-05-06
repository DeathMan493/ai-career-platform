from __future__ import annotations

import logging

from app.core.config import settings
from app.ingestion.mongo import get_database
from app.schemas.neo4j import Neo4jStatusPayload, Neo4jSyncPayload
from app.services.neo4j_service import neo4j_session
from app.services.progress_service import build_effective_profile
from app.services.recommendation_service import (
    get_course_recommendations,
    get_dashboard_recommendations,
    get_paper_recommendations,
)

logger = logging.getLogger(__name__)


def _load_effective_profile_document(firebase_uid: str) -> dict:
    document = get_database()["users"].find_one({"firebase_uid": firebase_uid})
    if not document:
        raise ValueError("User not found for Neo4j sync")
    return document


def get_neo4j_status() -> Neo4jStatusPayload:
    try:
        with neo4j_session() as session:
            result = session.run("RETURN 'connected' AS status").single()
        return Neo4jStatusPayload(
            connected=True,
            uri=settings.neo4j_uri,
            message=f"Neo4j connection successful: {result['status']}",
        )
    except Exception as exc:
        return Neo4jStatusPayload(
            connected=False,
            uri=settings.neo4j_uri,
            message="Neo4j connection unavailable.",
        )


def sync_user_graph(firebase_uid: str) -> Neo4jSyncPayload:
    document = _load_effective_profile_document(firebase_uid)
    profile = build_effective_profile(document)
    courses = get_course_recommendations(profile, limit=10)
    papers = get_paper_recommendations(profile, limit=10)
    dashboard = get_dashboard_recommendations(profile)
    jobs = dashboard.jobs

    relationship_count = 0

    with neo4j_session() as session:
        session.run(
            """
            MERGE (u:User {id: $id})
            SET u.name = $name,
                u.email = $email,
                u.career_goal = $career_goal
            """,
            id=profile.id,
            name=profile.name,
            email=document.get("email", ""),
            career_goal=profile.career_goal,
        )

        for skill in profile.skills:
            session.run(
                """
                MERGE (s:Skill {name: $skill})
                MERGE (u:User {id: $user_id})
                MERGE (u)-[:HAS_SKILL {level: $level}]->(s)
                """,
                user_id=profile.id,
                skill=skill.skill,
                level=skill.level,
            )
            relationship_count += 1

        for course in courses:
            session.run(
                """
                MERGE (c:Course {id: $id})
                SET c.title = $title,
                    c.provider = $provider,
                    c.level = $level,
                    c.duration = $duration
                MERGE (u:User {id: $user_id})
                MERGE (u)-[:RECOMMENDED_COURSE]->(c)
                """,
                user_id=profile.id,
                id=course.id,
                title=course.title,
                provider=course.provider,
                level=course.level,
                duration=course.duration,
            )
            relationship_count += 1
            for tag in course.tags:
                session.run(
                    """
                    MERGE (s:Skill {name: $skill})
                    MERGE (c:Course {id: $course_id})
                    MERGE (c)-[:COVERS]->(s)
                    """,
                    course_id=course.id,
                    skill=tag,
                )
                relationship_count += 1

        for paper in papers:
            session.run(
                """
                MERGE (p:Paper {id: $id})
                SET p.title = $title,
                    p.venue = $venue,
                    p.year = $year
                MERGE (u:User {id: $user_id})
                MERGE (u)-[:RECOMMENDED_PAPER]->(p)
                """,
                user_id=profile.id,
                id=paper.id,
                title=paper.title,
                venue=paper.venue,
                year=paper.year,
            )
            relationship_count += 1
            for tag in paper.tags:
                session.run(
                    """
                    MERGE (s:Skill {name: $skill})
                    MERGE (p:Paper {id: $paper_id})
                    MERGE (p)-[:RELATES_TO]->(s)
                    """,
                    paper_id=paper.id,
                    skill=tag,
                )
                relationship_count += 1

        for job in jobs:
            session.run(
                """
                MERGE (j:Job {id: $id})
                SET j.title = $title,
                    j.company = $company,
                    j.fit = $fit
                MERGE (u:User {id: $user_id})
                MERGE (u)-[:MATCHES_ROLE]->(j)
                """,
                user_id=profile.id,
                id=job.id,
                title=job.title,
                company=job.company,
                fit=job.fit,
            )
            relationship_count += 1
            for tag in job.tags:
                session.run(
                    """
                    MERGE (s:Skill {name: $skill})
                    MERGE (j:Job {id: $job_id})
                    MERGE (j)-[:REQUIRES]->(s)
                    """,
                    job_id=job.id,
                    skill=tag,
                )
                relationship_count += 1

    return Neo4jSyncPayload(
        user_id=profile.id,
        skill_count=len(profile.skills),
        course_count=len(courses),
        paper_count=len(papers),
        job_count=len(jobs),
        relationship_count=relationship_count,
    )


def sync_user_graph_if_available(firebase_uid: str) -> Neo4jSyncPayload | None:
    status = get_neo4j_status()
    if not status.connected:
        logger.warning("Skipping Neo4j sync because the graph database is unavailable.")
        return None

    try:
        return sync_user_graph(firebase_uid)
    except Exception:
        logger.warning("Automatic Neo4j sync failed.")
        return None
