from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_firebase_user, paginate_items
from app.schemas.common import ApiResponse, PaginatedPayload
from app.schemas.evaluation import EvaluationMetricsPayload, RecommendationExplanation
from app.services.evaluation_service import get_evaluation_metrics_by_uid, get_recommendation_explanations_by_uid

router = APIRouter()


@router.get("/metrics", response_model=ApiResponse[EvaluationMetricsPayload])
def get_metrics(current_user: dict = Depends(get_current_firebase_user)) -> ApiResponse[EvaluationMetricsPayload]:
    return ApiResponse(success=True, data=get_evaluation_metrics_by_uid(current_user["uid"]))


@router.get("/recommendations/explanations", response_model=ApiResponse[PaginatedPayload[RecommendationExplanation]])
def get_explanations(
    page: int = Query(default=1, ge=1, le=20),
    limit: int = Query(default=10, ge=1, le=20),
    current_user: dict = Depends(get_current_firebase_user),
) -> ApiResponse[PaginatedPayload[RecommendationExplanation]]:
    explanations = get_recommendation_explanations_by_uid(current_user["uid"])
    return ApiResponse(success=True, data=paginate_items(explanations, page=page, limit=limit))
