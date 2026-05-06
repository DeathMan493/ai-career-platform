from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_firebase_user, paginate_items
from app.schemas.common import ApiResponse, PaginatedPayload
from app.schemas.dashboard import CourseItem
from app.services.recommendation_service import get_course_recommendations
from app.services.user_service import get_effective_profile_by_uid

router = APIRouter()


@router.get("", response_model=ApiResponse[PaginatedPayload[CourseItem]])
def get_courses(
    page: int = Query(default=1, ge=1, le=50),
    limit: int = Query(default=10, ge=1, le=20),
    current_user: dict = Depends(get_current_firebase_user),
) -> ApiResponse[PaginatedPayload[CourseItem]]:
    profile = get_effective_profile_by_uid(current_user["uid"])
    requested_count = (page * limit) + 1
    recommendations = get_course_recommendations(profile, limit=requested_count)
    return ApiResponse(success=True, data=paginate_items(recommendations, page=page, limit=limit))
