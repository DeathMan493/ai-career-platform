from pydantic import BaseModel


class RoleSummary(BaseModel):
    title: str
    mission: str
    focus_areas: list[str]


class DashboardMetrics(BaseModel):
    profile_skill_count: int
    course_count: int
    paper_count: int
    job_count: int
    high_priority_gap_count: int
    readiness_score: int


class RecommendationItem(BaseModel):
    id: str
    title: str
    reason: str
    tags: list[str]


class CourseItem(RecommendationItem):
    provider: str
    level: str
    duration: str


class PaperItem(RecommendationItem):
    venue: str
    year: int


class JobItem(RecommendationItem):
    company: str
    fit: str


class MissingSkillItem(BaseModel):
    name: str
    priority: str
    progress: int
    reason: str


class DashboardPayload(BaseModel):
    role_summary: RoleSummary
    metrics: DashboardMetrics
    courses: list[CourseItem]
    papers: list[PaperItem]
    jobs: list[JobItem]
    recommendation_paths: list[str]
    missing_skills: list[MissingSkillItem]
