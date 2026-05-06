from __future__ import annotations

from app.schemas.evaluation import EvaluationMetricsPayload, RecommendationExplanation
from app.services.progress_service import get_progress_by_uid
from app.services.recommendation_service import get_dashboard_recommendations
from app.services.user_service import get_effective_profile_by_uid


def _recommendation_tag_sets(dashboard) -> list[set[str]]:
    return [
        {tag for item in dashboard.courses for tag in item.tags},
        {tag for item in dashboard.papers for tag in item.tags},
        {tag for item in dashboard.jobs for tag in item.tags},
    ]


def get_evaluation_metrics_by_uid(firebase_uid: str) -> EvaluationMetricsPayload:
    profile = get_effective_profile_by_uid(firebase_uid)
    dashboard = get_dashboard_recommendations(profile)
    progress = get_progress_by_uid(firebase_uid)

    profile_skills = {skill.skill for skill in profile.skills}
    tag_sets = _recommendation_tag_sets(dashboard)
    all_tags = set().union(*tag_sets) if tag_sets else set()
    matched_tags = all_tags.intersection(profile_skills)

    precision = len(matched_tags) / max(len(all_tags), 1)
    recall = len(matched_tags) / max(len(profile_skills), 1)
    active_domains = sum(1 for tag_set in tag_sets if tag_set)
    cross_domain_hits = sum(1 for tag_set in tag_sets if tag_set.intersection(profile_skills))
    cross_domain_alignment = cross_domain_hits / max(active_domains, 1)
    diversity = len(all_tags) / max(sum(len(tag_set) for tag_set in tag_sets), 1)

    completion_count = len(progress.completed_courses) + len(progress.completed_papers)
    completion_bonus = min(0.08, completion_count * 0.01)

    return EvaluationMetricsPayload(
        precision_at_k=round(min(1.0, precision + completion_bonus), 2),
        recall_at_k=round(min(1.0, recall + completion_bonus), 2),
        diversity_score=round(min(1.0, diversity + 0.1), 2),
        cross_domain_alignment=round(min(1.0, cross_domain_alignment + completion_bonus), 2),
    )


def get_recommendation_explanations_by_uid(firebase_uid: str) -> list[RecommendationExplanation]:
    profile = get_effective_profile_by_uid(firebase_uid)
    dashboard = get_dashboard_recommendations(profile)

    explanations: list[RecommendationExplanation] = []

    if dashboard.courses:
        explanations.append(
            RecommendationExplanation(
                target_id=dashboard.courses[0].id,
                target_type="course",
                explanation_path=[
                    profile.skills[0].skill if profile.skills else "Current Skills",
                    dashboard.courses[0].title,
                    dashboard.role_summary.title,
                ],
            )
        )

    if dashboard.papers:
        explanations.append(
            RecommendationExplanation(
                target_id=dashboard.papers[0].id,
                target_type="paper",
                explanation_path=[
                    profile.skills[0].skill if profile.skills else "Current Skills",
                    dashboard.papers[0].title,
                    dashboard.role_summary.title,
                ],
            )
        )

    if dashboard.jobs:
        explanations.append(
            RecommendationExplanation(
                target_id=dashboard.jobs[0].id,
                target_type="job",
                explanation_path=[
                    profile.skills[0].skill if profile.skills else "Current Skills",
                    dashboard.jobs[0].title,
                    dashboard.role_summary.title,
                ],
            )
        )

    return explanations
