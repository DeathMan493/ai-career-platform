from pydantic import BaseModel

from app.schemas.dashboard import CourseItem, PaperItem


class CompletedCourseItem(CourseItem):
    completed_at: str


class CompletedPaperItem(PaperItem):
    completed_at: str


class DerivedSkillItem(BaseModel):
    skill: str
    level: str
    progress: int


class SkillProgressItem(BaseModel):
    skill: str
    progress: int


class UserProgressPayload(BaseModel):
    completed_courses: list[CompletedCourseItem]
    completed_papers: list[CompletedPaperItem]
    derived_skills: list[DerivedSkillItem]
    skill_progress: list[SkillProgressItem]


class CompletionRemoveRequest(BaseModel):
    item_id: str
