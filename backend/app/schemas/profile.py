from pydantic import BaseModel


class SkillItem(BaseModel):
    skill: str
    level: str


class ProfilePayload(BaseModel):
    id: str
    name: str
    career_goal: str
    skills: list[SkillItem]


class UpdateProfileRequest(BaseModel):
    career_goal: str
    skills: list[SkillItem]
