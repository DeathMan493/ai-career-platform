from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_firebase_user, paginate_items
from app.schemas.common import ApiResponse, PaginatedPayload
from app.services.skill_service import get_skill_suggestions

router = APIRouter()


@router.get("/suggest", response_model=ApiResponse[PaginatedPayload[str]])
def suggest_skills(
    q: str = Query(default="", max_length=80),
    page: int = Query(default=1, ge=1, le=20),
    limit: int = Query(default=8, ge=1, le=12),
    _: dict = Depends(get_current_firebase_user),
) -> ApiResponse[PaginatedPayload[str]]:
    requested_count = (page * limit) + 1
    suggestions = get_skill_suggestions(q=q, limit=requested_count)
    return ApiResponse(success=True, data=paginate_items(suggestions, page=page, limit=limit))
