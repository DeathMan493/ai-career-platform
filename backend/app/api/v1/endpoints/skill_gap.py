from fastapi import APIRouter, Depends

from app.api.deps import get_current_firebase_user
from app.schemas.common import ApiResponse
from app.schemas.skill_gap import SkillGapPayload
from app.services.recommendation_service import get_skill_gap_recommendations
from app.services.user_service import get_effective_profile_by_uid

router = APIRouter()


@router.get("", response_model=ApiResponse[SkillGapPayload])
def get_skill_gap(current_user: dict = Depends(get_current_firebase_user)) -> ApiResponse[SkillGapPayload]:
    profile = get_effective_profile_by_uid(current_user["uid"])
    return ApiResponse(success=True, data=get_skill_gap_recommendations(profile))
