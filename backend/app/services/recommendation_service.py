from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import re
from typing import Any

from pymongo.collection import Collection

from app.ingestion.mongo import get_database
from app.schemas.dashboard import (
    CourseItem,
    DashboardMetrics,
    DashboardPayload,
    JobItem,
    MissingSkillItem,
    PaperItem,
    RoleSummary,
)
from app.schemas.graph import GraphEdge, GraphLegend, GraphNode, GraphPayload
from app.schemas.profile import ProfilePayload
from app.schemas.skill_gap import FocusBridgeItem, MissingSkillItem as SkillGapMissingSkillItem, RoadmapStep, SkillGapBridges, SkillGapPayload
from app.services.neo4j_recommendation_service import (
    get_course_recommendations_from_graph,
    get_job_recommendations_from_graph,
    get_missing_skills_from_graph,
    get_paper_recommendations_from_graph,
)


FOCUS_AREAS_BY_GOAL = {
    "AI Researcher": ["Representation learning", "Research communication", "Model evaluation"],
    "Machine Learning Engineer": ["Model development", "Deployment readiness", "Data pipelines"],
    "Data Scientist": ["Statistical modeling", "Experimentation", "Business intelligence"],
}

MISSION_BY_GOAL = {
    "AI Researcher": "Blend advanced learning, research depth, and explainable recommendation logic into a focused AI career path.",
    "Machine Learning Engineer": "Strengthen practical machine learning, systems thinking, and delivery skills for production-ready AI work.",
    "Data Scientist": "Build a balanced path across analytics, modeling, and communication for data-driven decision making.",
}

GOAL_KEYWORDS = {
    "AI Researcher": {
        "artificial intelligence", "machine learning", "deep learning", "representation learning",
        "knowledge graphs", "graph neural networks", "research", "evaluation", "recommendation systems",
    },
    "Machine Learning Engineer": {
        "machine learning", "deep learning", "mlops", "deployment", "data pipelines",
        "tensorflow", "pytorch", "python", "cloud computing", "model evaluation",
    },
    "Data Scientist": {
        "data science", "statistics", "data analysis", "machine learning", "sql",
        "data visualization", "experimentation", "analytics", "python",
    },
}

ASCII_TITLE_PATTERN = re.compile(r"^[\x00-\x7F]+$")
CURRENT_YEAR = datetime.now().year
PAPER_RECENCY_CUTOFF_YEAR = CURRENT_YEAR - 3

NODE_X = {
    "user": 10,
    "skill": 28,
    "course": 48,
    "paper": 68,
    "job": 88,
}
NODE_Y = {
    "user": [50],
    "skill": [38, 62],
    "course": [38, 62],
    "paper": [38, 62],
    "job": [50],
}


@dataclass
class ScoredDocument:
    document: dict[str, Any]
    overlap: list[str]
    score: float


def _short_label(value: str, max_length: int = 24) -> str:
    if len(value) <= max_length:
        return value
    return value[: max_length - 1].rstrip() + "?"


def _normalize_profile_skills(profile: ProfilePayload) -> set[str]:
    normalized: set[str] = set()
    for item in profile.skills:
        name = item.skill.strip()
        if name:
            normalized.add(name)
    return normalized


def _normalize_terms(values: list[str] | set[str] | None) -> set[str]:
    normalized: set[str] = set()
    for value in values or []:
        cleaned = value.strip().casefold()
        if cleaned:
            normalized.add(cleaned)
    return normalized


def _goal_keywords(profile: ProfilePayload) -> set[str]:
    return GOAL_KEYWORDS.get(profile.career_goal or "", set())


def _has_ascii_title(title: str | None) -> bool:
    if not title:
        return False
    return bool(ASCII_TITLE_PATTERN.match(title))


def _is_valid_course(document: dict[str, Any]) -> bool:
    title = (document.get("title") or "").strip()
    return bool(title) and _has_ascii_title(title)


def _is_valid_paper(document: dict[str, Any]) -> bool:
    title = (document.get("title") or "").strip()
    publication_year = int(document.get("publication_year") or 0)
    return bool(title) and _has_ascii_title(title) and publication_year >= PAPER_RECENCY_CUTOFF_YEAR


def _score_documents(
    collection: Collection,
    profile: ProfilePayload,
    limit: int,
    *,
    kind: str,
) -> list[ScoredDocument]:
    scored: list[ScoredDocument] = []
    profile_skills = _normalize_profile_skills(profile)
    goal_terms = _goal_keywords(profile)
    cursor = collection.find({}, {"title": 1, "provider": 1, "difficulty": 1, "duration": 1, "organization": 1, "publication_year": 1, "primary_location": 1, "source_id": 1, "url": 1, "normalized_skills": 1, "keywords": 1, "qualification_summary": 1, "description": 1})

    for document in cursor:
        if kind == "course" and not _is_valid_course(document):
            continue
        if kind == "paper" and not _is_valid_paper(document):
            continue

        normalized_skills = [skill for skill in (document.get("normalized_skills") or []) if skill]
        overlap = sorted(profile_skills.intersection(normalized_skills))
        coverage = len(overlap)
        skill_diversity_bonus = min(len(normalized_skills), 6) * 0.05
        score = (coverage * 2.0) + skill_diversity_bonus

        document_terms = _normalize_terms(normalized_skills)
        document_terms.update(_normalize_terms(document.get("keywords") or []))
        goal_overlap = len(goal_terms.intersection(document_terms))
        if goal_overlap:
            score += goal_overlap * 1.25

        if coverage == 0:
            score += 0.1
        if kind == "paper":
            publication_year = int(document.get("publication_year") or 0)
            score += max(0, publication_year - PAPER_RECENCY_CUTOFF_YEAR) * 0.4
        scored.append(ScoredDocument(document=document, overlap=overlap, score=score))

    scored.sort(key=lambda item: (-item.score, -len(item.overlap), item.document.get("title") or ""))
    return scored[:limit]


def _collect_missing_skills(profile_skills: set[str], scored_sets: list[list[ScoredDocument]], limit: int = 4) -> list[tuple[str, int]]:
    counts: dict[str, int] = {}
    for scored_group in scored_sets:
        for scored in scored_group[:3]:
            for skill in scored.document.get("normalized_skills") or []:
                if skill in profile_skills:
                    continue
                counts[skill] = counts.get(skill, 0) + 1

    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return ranked[:limit]


def _build_reason(overlap: list[str], fallback: str) -> str:
    if overlap:
        return f"Matches your current skills in {', '.join(overlap[:3])}."
    return fallback


def _build_courses(scored_courses: list[ScoredDocument], limit: int) -> list[CourseItem]:
    items: list[CourseItem] = []
    seen_titles: set[str] = set()
    for scored in scored_courses:
        document = scored.document
        title = document.get("title") or "Untitled Course"
        normalized_title = title.strip().casefold()
        if normalized_title in seen_titles:
            continue
        seen_titles.add(normalized_title)
        items.append(
            CourseItem(
                id=str(document.get("source_id") or document.get("_id") or document.get("title")),
                title=title,
                provider=document.get("provider") or "Unknown Provider",
                level=document.get("difficulty") or "Flexible",
                duration=document.get("duration") or "Self-paced",
                reason=_build_reason(scored.overlap, "Expands your skill graph toward stronger course-job-paper alignment."),
                tags=(document.get("normalized_skills") or [])[:3],
            )
        )
        if len(items) >= limit:
            break
    return items


def _build_papers(scored_papers: list[ScoredDocument], limit: int) -> list[PaperItem]:
    items: list[PaperItem] = []
    seen_titles: set[str] = set()
    for scored in scored_papers:
        document = scored.document
        title = document.get("title") or "Untitled Paper"
        normalized_title = title.strip().casefold()
        if normalized_title in seen_titles:
            continue
        seen_titles.add(normalized_title)
        venue = ((document.get("primary_location") or {}).get("source") or {}).get("display_name") or "OpenAlex"
        items.append(
            PaperItem(
                id=str(document.get("source_id") or document.get("_id") or document.get("title")),
                title=title,
                venue=venue,
                year=int(document.get("publication_year") or 0),
                reason=_build_reason(scored.overlap, "Supports the technical and research ideas connected to your target role."),
                tags=(document.get("normalized_skills") or document.get("keywords") or [])[:3],
            )
        )
        if len(items) >= limit:
            break
    return items


def get_course_recommendations(profile: ProfilePayload, limit: int = 10) -> list[CourseItem]:
    graph_items = get_course_recommendations_from_graph(profile, limit=limit)
    if graph_items:
        return graph_items[:limit]

    database = get_database()
    scored_courses = _score_documents(database["courses"], profile, limit=max(limit * 3, 12), kind="course")
    return _build_courses(scored_courses, limit=limit)[:limit]


def get_paper_recommendations(profile: ProfilePayload, limit: int = 10) -> list[PaperItem]:
    graph_items = get_paper_recommendations_from_graph(profile, limit=limit)
    if graph_items:
        return graph_items[:limit]

    database = get_database()
    scored_papers = _score_documents(database["papers"], profile, limit=max(limit * 3, 12), kind="paper")
    return _build_papers(scored_papers, limit=limit)[:limit]


def get_job_recommendations(profile: ProfilePayload, limit: int = 3) -> list[JobItem]:
    graph_items = get_job_recommendations_from_graph(profile, limit=limit)
    if graph_items:
        return graph_items[:limit]

    database = get_database()
    scored_jobs = _score_documents(database["jobs"], profile, limit=max(limit * 3, 9), kind="job")
    return _build_jobs(scored_jobs)[:limit]


def get_missing_skill_recommendations(profile: ProfilePayload, limit: int = 4) -> list[MissingSkillItem]:
    graph_items = get_missing_skills_from_graph(profile, limit=limit)
    if graph_items:
        return graph_items[:limit]

    database = get_database()
    profile_skills = _normalize_profile_skills(profile)
    scored_courses = _score_documents(database["courses"], profile, limit=18, kind="course")
    scored_papers = _score_documents(database["papers"], profile, limit=18, kind="paper")
    scored_jobs = _score_documents(database["jobs"], profile, limit=12, kind="job")
    return _build_missing_skills(profile_skills, scored_courses, scored_papers, scored_jobs)


def _build_jobs(scored_jobs: list[ScoredDocument]) -> list[JobItem]:
    items: list[JobItem] = []
    for scored in scored_jobs[:3]:
        document = scored.document
        fit = "Target fit" if len(scored.overlap) >= 3 else "Strong fit" if len(scored.overlap) >= 2 else "Emerging fit"
        items.append(
            JobItem(
                id=str(document.get("source_id") or document.get("_id") or document.get("title")),
                title=document.get("title") or "Untitled Job",
                company=document.get("organization") or "USAJOBS",
                fit=fit,
                reason=_build_reason(scored.overlap, "Represents a role that your current profile can grow toward."),
                tags=(document.get("normalized_skills") or [])[:3],
            )
        )
    return items


def _build_missing_skills(profile_skills: set[str], scored_courses: list[ScoredDocument], scored_papers: list[ScoredDocument], scored_jobs: list[ScoredDocument]) -> list[MissingSkillItem]:
    ranked = _collect_missing_skills(profile_skills, [scored_courses, scored_papers, scored_jobs])
    results: list[MissingSkillItem] = []
    for index, (skill, count) in enumerate(ranked):
        priority = "High" if count >= 3 or index < 2 else "Medium"
        progress = min(70, 25 + (count * 12))
        results.append(
            MissingSkillItem(
                name=skill,
                priority=priority,
                progress=progress,
                reason="Appears repeatedly across recommended courses, papers, and jobs, so strengthening it should improve cross-domain alignment.",
            )
        )
    return results


def _build_role_summary(profile: ProfilePayload) -> RoleSummary:
    goal = profile.career_goal or "AI Researcher"
    return RoleSummary(
        title=goal,
        mission=MISSION_BY_GOAL.get(goal, "Build a stronger bridge between current skills, learning resources, research material, and career opportunities."),
        focus_areas=FOCUS_AREAS_BY_GOAL.get(goal, ["Skill growth", "Research alignment", "Career readiness"]),
    )


def _build_recommendation_paths(profile_skills: set[str], courses: list[CourseItem], papers: list[PaperItem], jobs: list[JobItem], missing_skills: list[MissingSkillItem], career_goal: str) -> list[str]:
    paths: list[str] = []
    sorted_skills = sorted(profile_skills)
    leading_skill = sorted_skills[0] if sorted_skills else "Current skills"
    if courses and jobs:
        paths.append(f"{leading_skill} -> {courses[0].title} -> {jobs[0].title}")
    if len(sorted_skills) > 1 and papers and jobs:
        second_skill = sorted_skills[1]
        paths.append(f"{second_skill} -> {papers[0].title} -> {jobs[0].title}")
    if missing_skills and courses:
        paths.append(f"{missing_skills[0].name} -> {courses[0].title} -> {career_goal}")
    return paths[:3]


def _empty_dashboard_payload(profile: ProfilePayload) -> DashboardPayload:
    role_summary = _build_role_summary(profile)
    return DashboardPayload(
        role_summary=role_summary,
        metrics=DashboardMetrics(
            profile_skill_count=len(profile.skills),
            course_count=0,
            paper_count=0,
            job_count=0,
            high_priority_gap_count=0,
            readiness_score=max(20, min(92, len(profile.skills) * 12)),
        ),
        courses=[],
        papers=[],
        jobs=[],
        recommendation_paths=[],
        missing_skills=[],
    )


def _empty_skill_gap_payload(profile: ProfilePayload) -> SkillGapPayload:
    role_summary = _build_role_summary(profile)
    return SkillGapPayload(
        career_goal=role_summary.title,
        summary=role_summary.mission,
        focus_areas=role_summary.focus_areas,
        current_skill_count=len(profile.skills),
        gap_count=0,
        missing_skills=[],
        roadmap=[
            RoadmapStep(
                phase="Profile captured",
                timeline="Now",
                action="Add more skills or import more recommendation data to generate deeper gap analysis.",
            )
        ],
        bridges=SkillGapBridges(courses=[], papers=[], jobs=[]),
    )


def _empty_graph_payload(profile: ProfilePayload) -> GraphPayload:
    role_summary = _build_role_summary(profile)
    return GraphPayload(
        career_goal=role_summary.title,
        nodes=[GraphNode(id="user", label="User", type="user", x=NODE_X["user"], y=NODE_Y["user"][0])],
        edges=[],
        recommendation_paths=[],
        legend=GraphLegend(
            user="User profile and goal",
            skill="Current skill from profile",
            course="Recommended course from backend",
            paper="Recommended paper from backend",
            job="Recommended career role from backend",
        ),
    )


def get_dashboard_recommendations(profile: ProfilePayload) -> DashboardPayload:
    try:
        profile_skills = _normalize_profile_skills(profile)
        courses = get_course_recommendations(profile, limit=3)
        papers = get_paper_recommendations(profile, limit=3)
        jobs = get_job_recommendations(profile, limit=3)
        missing_skills = get_missing_skill_recommendations(profile, limit=4)
        role_summary = _build_role_summary(profile)
        recommendation_paths = _build_recommendation_paths(profile_skills, courses, papers, jobs, missing_skills, role_summary.title)
        readiness_score = max(30, min(92, int((len(profile_skills) * 11) + (len(courses) * 3) - (len(missing_skills) * 4))))

        return DashboardPayload(
            role_summary=role_summary,
            metrics=DashboardMetrics(
                profile_skill_count=len(profile.skills),
                course_count=len(courses),
                paper_count=len(papers),
                job_count=len(jobs),
                high_priority_gap_count=sum(1 for skill in missing_skills if skill.priority == "High"),
                readiness_score=readiness_score,
            ),
            courses=courses,
            papers=papers,
            jobs=jobs,
            recommendation_paths=recommendation_paths,
            missing_skills=missing_skills,
        )
    except Exception:
        return _empty_dashboard_payload(profile)


def get_skill_gap_recommendations(profile: ProfilePayload) -> SkillGapPayload:
    try:
        dashboard = get_dashboard_recommendations(profile)
        roadmap = [
            RoadmapStep(phase="Strengthen technical foundations", timeline="Weeks 1-3", action=f"Focus on {dashboard.missing_skills[0].name if dashboard.missing_skills else 'high-priority skills'} through targeted study and hands-on exercises."),
            RoadmapStep(phase="Connect learning to research", timeline="Weeks 4-6", action="Use recommended papers to deepen the concepts that appear repeatedly across your course and job matches."),
            RoadmapStep(phase="Move toward role readiness", timeline="Weeks 7-9", action="Translate improved skills into portfolio projects and applications aligned with the suggested jobs."),
        ]
        return SkillGapPayload(
            career_goal=dashboard.role_summary.title,
            summary=dashboard.role_summary.mission,
            focus_areas=dashboard.role_summary.focus_areas,
            current_skill_count=dashboard.metrics.profile_skill_count,
            gap_count=len(dashboard.missing_skills),
            missing_skills=[
                SkillGapMissingSkillItem(name=item.name, priority=item.priority, progress=item.progress, reason=item.reason)
                for item in dashboard.missing_skills
            ],
            roadmap=roadmap,
            bridges=SkillGapBridges(
                courses=[FocusBridgeItem(id=item.id, title=item.title, reason=item.reason) for item in dashboard.courses[:2]],
                papers=[FocusBridgeItem(id=item.id, title=item.title, reason=item.reason) for item in dashboard.papers[:2]],
                jobs=[FocusBridgeItem(id=item.id, title=item.title, reason=item.reason) for item in dashboard.jobs[:2]],
            ),
        )
    except Exception:
        return _empty_skill_gap_payload(profile)


def _graph_nodes_from_dashboard(profile: ProfilePayload, dashboard: DashboardPayload) -> list[GraphNode]:
    nodes: list[GraphNode] = [GraphNode(id="user", label="User", type="user", x=NODE_X["user"], y=NODE_Y["user"][0])]
    user_skills = sorted(_normalize_profile_skills(profile))[:2]

    for index, skill_name in enumerate(user_skills):
        nodes.append(
            GraphNode(
                id=f"skill_{index}",
                label=_short_label(skill_name),
                type="skill",
                x=NODE_X["skill"],
                y=NODE_Y["skill"][index % 2],
            )
        )

    for index, course in enumerate(dashboard.courses[:2]):
        nodes.append(
            GraphNode(
                id=f"course_{index}",
                label=_short_label(course.title),
                type="course",
                x=NODE_X["course"],
                y=NODE_Y["course"][index % 2],
            )
        )

    for index, paper in enumerate(dashboard.papers[:2]):
        nodes.append(
            GraphNode(
                id=f"paper_{index}",
                label=_short_label(paper.title),
                type="paper",
                x=NODE_X["paper"],
                y=NODE_Y["paper"][index % 2],
            )
        )

    if dashboard.jobs:
        nodes.append(
            GraphNode(
                id="job_0",
                label=_short_label(dashboard.jobs[0].title),
                type="job",
                x=NODE_X["job"],
                y=NODE_Y["job"][0],
            )
        )

    return nodes


def _graph_edges_from_dashboard(profile: ProfilePayload, dashboard: DashboardPayload) -> list[GraphEdge]:
    edges: list[GraphEdge] = []
    user_skills = sorted(_normalize_profile_skills(profile))[:2]

    for index, _skill_name in enumerate(user_skills):
        edges.append(GraphEdge(from_="user", to=f"skill_{index}", label="has skill"))

    if user_skills and dashboard.courses:
        edges.append(GraphEdge(from_="skill_0", to="course_0", label="matches"))
    if len(user_skills) > 1 and len(dashboard.courses) > 1:
        edges.append(GraphEdge(from_="skill_1", to="course_1", label="supports"))
    if dashboard.courses and dashboard.papers:
        edges.append(GraphEdge(from_="course_0", to="paper_0", label="informs"))
    if len(dashboard.courses) > 1 and len(dashboard.papers) > 1:
        edges.append(GraphEdge(from_="course_1", to="paper_1", label="extends"))
    if dashboard.papers and dashboard.jobs:
        edges.append(GraphEdge(from_="paper_0", to="job_0", label="aligns with"))
    if len(dashboard.papers) > 1 and dashboard.jobs:
        edges.append(GraphEdge(from_="paper_1", to="job_0", label="strengthens"))

    return edges


def get_graph_recommendations(profile: ProfilePayload) -> GraphPayload:
    try:
        dashboard = get_dashboard_recommendations(profile)
        return GraphPayload(
            career_goal=dashboard.role_summary.title,
            nodes=_graph_nodes_from_dashboard(profile, dashboard),
            edges=_graph_edges_from_dashboard(profile, dashboard),
            recommendation_paths=dashboard.recommendation_paths,
            legend=GraphLegend(
                user="User profile and goal",
                skill="Current skill from profile",
                course="Recommended course from MongoDB",
                paper="Recommended paper from MongoDB",
                job="Recommended career role from MongoDB",
            ),
        )
    except Exception:
        return _empty_graph_payload(profile)
