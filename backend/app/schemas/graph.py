from pydantic import BaseModel, ConfigDict, Field


class GraphNode(BaseModel):
    id: str
    label: str
    type: str
    x: int
    y: int


class GraphEdge(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    from_: str = Field(alias="from")
    to: str
    label: str


class GraphLegend(BaseModel):
    user: str
    skill: str
    course: str
    paper: str
    job: str


class GraphPayload(BaseModel):
    career_goal: str
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    recommendation_paths: list[str]
    legend: GraphLegend
