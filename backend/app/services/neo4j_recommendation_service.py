from __future__ import annotations

import logging

from app.schemas.dashboard import CourseItem, JobItem, MissingSkillItem, PaperItem
from app.schemas.profile import ProfilePayload
from app.services.neo4j_service import neo4j_session

logger = logging.getLogger(__name__)
_neo4j_available = True


def _graph_contains(required_labels: set[str], required_relationships: set[str]) -> bool:
    try:
        with neo4j_session() as session:
            labels = {row["label"] for row in session.run("CALL db.labels() YIELD label RETURN label")}
            relationship_types = {
                row["relationshipType"]
                for row in session.run("CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType")
            }
    except Exception:
        return False

    return required_labels.issubset(labels) and required_relationships.issubset(relationship_types)


def _run_query(query: str, *, required_labels: set[str], required_relationships: set[str], **params) -> list[dict]:
    global _neo4j_available
    if not _neo4j_available:
        return []

    if not _graph_contains(required_labels, required_relationships):
        return []

    try:
        with neo4j_session() as session:
            return [record.data() for record in session.run(query, **params)]
    except Exception:
        _neo4j_available = False
        logger.warning("Neo4j recommendation query failed.")
        return []


def get_course_recommendations_from_graph(profile: ProfilePayload, limit: int = 10) -> list[CourseItem]:
    rows = _run_query(
        """
        MATCH (u:User {id: $user_id})-[:RECOMMENDED_COURSE]->(c:Course)
        OPTIONAL MATCH (u)-[:HAS_SKILL]->(matched:Skill)<-[:COVERS]-(c)
        OPTIONAL MATCH (c)-[:COVERS]->(covered:Skill)
        WITH c,
             collect(DISTINCT matched.name) AS matched_skills,
             collect(DISTINCT covered.name) AS covered_skills,
             count(DISTINCT matched) AS overlap
        RETURN c.id AS id,
               c.title AS title,
               c.provider AS provider,
               c.level AS level,
               c.duration AS duration,
               matched_skills,
               covered_skills,
               overlap
        ORDER BY overlap DESC, size(covered_skills) DESC, c.title ASC
        LIMIT $limit
        """,
        required_labels={"User", "Course", "Skill"},
        required_relationships={"RECOMMENDED_COURSE", "HAS_SKILL", "COVERS"},
        user_id=profile.id,
        limit=limit,
    )

    items: list[CourseItem] = []
    seen_titles: set[str] = set()
    for row in rows:
        title = row.get("title") or "Untitled Course"
        normalized_title = title.strip().casefold()
        if normalized_title in seen_titles:
            continue
        seen_titles.add(normalized_title)

        matched_skills = [skill for skill in (row.get("matched_skills") or []) if skill]
        covered_skills = [skill for skill in (row.get("covered_skills") or []) if skill]
        reason = (
            f"Graph match across {', '.join(matched_skills[:3])}."
            if matched_skills
            else "Retrieved from your Neo4j skill-course graph neighborhood."
        )

        items.append(
            CourseItem(
                id=str(row.get("id") or title),
                title=title,
                provider=row.get("provider") or "Unknown Provider",
                level=row.get("level") or "Flexible",
                duration=row.get("duration") or "Self-paced",
                reason=reason,
                tags=covered_skills[:3],
            )
        )

    return items


def get_paper_recommendations_from_graph(profile: ProfilePayload, limit: int = 10) -> list[PaperItem]:
    rows = _run_query(
        """
        MATCH (u:User {id: $user_id})-[:RECOMMENDED_PAPER]->(p:Paper)
        OPTIONAL MATCH (u)-[:HAS_SKILL]->(matched:Skill)<-[:RELATES_TO]-(p)
        OPTIONAL MATCH (p)-[:RELATES_TO]->(related:Skill)
        WITH p,
             collect(DISTINCT matched.name) AS matched_skills,
             collect(DISTINCT related.name) AS related_skills,
             count(DISTINCT matched) AS overlap
        RETURN p.id AS id,
               p.title AS title,
               p.venue AS venue,
               p.year AS year,
               matched_skills,
               related_skills,
               overlap
        ORDER BY overlap DESC, p.year DESC, p.title ASC
        LIMIT $limit
        """,
        required_labels={"User", "Paper", "Skill"},
        required_relationships={"RECOMMENDED_PAPER", "HAS_SKILL", "RELATES_TO"},
        user_id=profile.id,
        limit=limit,
    )

    items: list[PaperItem] = []
    seen_titles: set[str] = set()
    for row in rows:
        title = row.get("title") or "Untitled Paper"
        normalized_title = title.strip().casefold()
        if normalized_title in seen_titles:
            continue
        seen_titles.add(normalized_title)

        matched_skills = [skill for skill in (row.get("matched_skills") or []) if skill]
        related_skills = [skill for skill in (row.get("related_skills") or []) if skill]
        reason = (
            f"Graph match across {', '.join(matched_skills[:3])}."
            if matched_skills
            else "Retrieved from your Neo4j research graph neighborhood."
        )

        items.append(
            PaperItem(
                id=str(row.get("id") or title),
                title=title,
                venue=row.get("venue") or "Neo4j",
                year=int(row.get("year") or 0),
                reason=reason,
                tags=related_skills[:3],
            )
        )

    return items


def get_job_recommendations_from_graph(profile: ProfilePayload, limit: int = 3) -> list[JobItem]:
    rows = _run_query(
        """
        MATCH (u:User {id: $user_id})-[:MATCHES_ROLE]->(j:Job)
        OPTIONAL MATCH (u)-[:HAS_SKILL]->(matched:Skill)<-[:REQUIRES]-(j)
        OPTIONAL MATCH (j)-[:REQUIRES]->(required:Skill)
        WITH j,
             collect(DISTINCT matched.name) AS matched_skills,
             collect(DISTINCT required.name) AS required_skills,
             count(DISTINCT matched) AS overlap
        RETURN j.id AS id,
               j.title AS title,
               j.company AS company,
               j.fit AS fit,
               matched_skills,
               required_skills,
               overlap
        ORDER BY overlap DESC, j.title ASC
        LIMIT $limit
        """,
        required_labels={"User", "Job", "Skill"},
        required_relationships={"MATCHES_ROLE", "HAS_SKILL", "REQUIRES"},
        user_id=profile.id,
        limit=limit,
    )

    items: list[JobItem] = []
    for row in rows:
        matched_skills = [skill for skill in (row.get("matched_skills") or []) if skill]
        required_skills = [skill for skill in (row.get("required_skills") or []) if skill]
        reason = (
            f"Graph match across {', '.join(matched_skills[:3])}."
            if matched_skills
            else "Retrieved from your Neo4j career graph neighborhood."
        )

        items.append(
            JobItem(
                id=str(row.get("id") or row.get("title") or "job"),
                title=row.get("title") or "Untitled Job",
                company=row.get("company") or "Neo4j",
                fit=row.get("fit") or "Emerging fit",
                reason=reason,
                tags=required_skills[:3],
            )
        )

    return items


def get_missing_skills_from_graph(profile: ProfilePayload, limit: int = 4) -> list[MissingSkillItem]:
    rows = _run_query(
        """
        MATCH (u:User {id: $user_id})
        OPTIONAL MATCH (u)-[:HAS_SKILL]->(owned:Skill)
        WITH u, collect(DISTINCT owned.name) AS owned_skills
        CALL (u) {
            MATCH (u)-[:RECOMMENDED_COURSE]->(:Course)-[:COVERS]->(s:Skill)
            RETURN s.name AS skill, 1 AS support
            UNION ALL
            MATCH (u)-[:RECOMMENDED_PAPER]->(:Paper)-[:RELATES_TO]->(s:Skill)
            RETURN s.name AS skill, 1 AS support
            UNION ALL
            MATCH (u)-[:MATCHES_ROLE]->(:Job)-[:REQUIRES]->(s:Skill)
            RETURN s.name AS skill, 1 AS support
        }
        WITH owned_skills, skill, sum(support) AS support
        WHERE skill IS NOT NULL AND NOT skill IN owned_skills
        RETURN skill, support
        ORDER BY support DESC, skill ASC
        LIMIT $limit
        """,
        required_labels={"User", "Course", "Paper", "Job", "Skill"},
        required_relationships={
            "HAS_SKILL",
            "RECOMMENDED_COURSE",
            "COVERS",
            "RECOMMENDED_PAPER",
            "RELATES_TO",
            "MATCHES_ROLE",
            "REQUIRES",
        },
        user_id=profile.id,
        limit=limit,
    )

    items: list[MissingSkillItem] = []
    for index, row in enumerate(rows):
        skill = row.get("skill")
        support = int(row.get("support") or 0)
        if not skill:
            continue
        priority = "High" if support >= 3 or index < 2 else "Medium"
        progress = min(70, 25 + (support * 12))
        items.append(
            MissingSkillItem(
                name=skill,
                priority=priority,
                progress=progress,
                reason="Appears repeatedly in your Neo4j course, paper, and job graph neighborhoods.",
            )
        )

    return items
