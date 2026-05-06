from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_firebase_user, paginate_items
from app.schemas.common import ApiResponse, PaginatedPayload
from app.schemas.dashboard import PaperItem
from app.services.recommendation_service import get_paper_recommendations
from app.services.user_service import get_effective_profile_by_uid

router = APIRouter()


@router.get("", response_model=ApiResponse[PaginatedPayload[PaperItem]])
def get_papers(
    page: int = Query(default=1, ge=1, le=50),
    limit: int = Query(default=10, ge=1, le=20),
    current_user: dict = Depends(get_current_firebase_user),
) -> ApiResponse[PaginatedPayload[PaperItem]]:
    profile = get_effective_profile_by_uid(current_user["uid"])
    requested_count = (page * limit) + 1
    recommendations = get_paper_recommendations(profile, limit=requested_count)
    return ApiResponse(success=True, data=paginate_items(recommendations, page=page, limit=limit))
