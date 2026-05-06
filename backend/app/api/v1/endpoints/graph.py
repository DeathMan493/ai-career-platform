from fastapi import APIRouter, Depends

from app.api.deps import get_current_firebase_user
from app.schemas.common import ApiResponse
from app.schemas.graph import GraphPayload
from app.services.recommendation_service import get_graph_recommendations
from app.services.user_service import get_effective_profile_by_uid

router = APIRouter()


@router.get("", response_model=ApiResponse[GraphPayload])
def get_graph_view(current_user: dict = Depends(get_current_firebase_user)) -> ApiResponse[GraphPayload]:
    profile = get_effective_profile_by_uid(current_user["uid"])
    return ApiResponse(success=True, data=get_graph_recommendations(profile))
