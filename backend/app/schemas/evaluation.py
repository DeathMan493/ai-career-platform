from pydantic import BaseModel


class EvaluationMetricsPayload(BaseModel):
    precision_at_k: float
    recall_at_k: float
    diversity_score: float
    cross_domain_alignment: float


class RecommendationExplanation(BaseModel):
    target_id: str
    target_type: str
    explanation_path: list[str]
