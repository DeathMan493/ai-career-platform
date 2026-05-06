from pydantic import BaseModel


class FocusBridgeItem(BaseModel):
    id: str
    title: str
    reason: str


class MissingSkillItem(BaseModel):
    name: str
    priority: str
    progress: int
    reason: str


class RoadmapStep(BaseModel):
    phase: str
    timeline: str
    action: str


class SkillGapBridges(BaseModel):
    courses: list[FocusBridgeItem]
    papers: list[FocusBridgeItem]
    jobs: list[FocusBridgeItem]


class SkillGapPayload(BaseModel):
    career_goal: str
    summary: str
    focus_areas: list[str]
    current_skill_count: int
    gap_count: int
    missing_skills: list[MissingSkillItem]
    roadmap: list[RoadmapStep]
    bridges: SkillGapBridges
