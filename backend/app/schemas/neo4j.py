from pydantic import BaseModel


class Neo4jStatusPayload(BaseModel):
    connected: bool
    uri: str
    message: str


class Neo4jSyncPayload(BaseModel):
    user_id: str
    skill_count: int
    course_count: int
    paper_count: int
    job_count: int
    relationship_count: int
