from fastapi import APIRouter, Depends

from app.api.deps import get_current_firebase_user
from app.schemas.common import ApiResponse
from app.schemas.dashboard import DashboardPayload
from app.services.recommendation_service import get_dashboard_recommendations
from app.services.user_service import get_effective_profile_by_uid

router = APIRouter()


@router.get("", response_model=ApiResponse[DashboardPayload])
def get_dashboard(current_user: dict = Depends(get_current_firebase_user)) -> ApiResponse[DashboardPayload]:
    profile = get_effective_profile_by_uid(current_user["uid"])
    return ApiResponse(success=True, data=get_dashboard_recommendations(profile))
