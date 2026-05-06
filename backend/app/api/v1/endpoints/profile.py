from fastapi import APIRouter, Depends

from app.api.deps import get_current_firebase_user
from app.schemas.common import ApiResponse
from app.schemas.profile import ProfilePayload, UpdateProfileRequest
from app.services.user_service import get_profile_by_uid, update_profile_by_uid

router = APIRouter()


@router.get("/me", response_model=ApiResponse[ProfilePayload])
def get_my_profile(current_user: dict = Depends(get_current_firebase_user)) -> ApiResponse[ProfilePayload]:
    profile = get_profile_by_uid(current_user["uid"])
    return ApiResponse(success=True, data=profile)


@router.put("/me", response_model=ApiResponse[ProfilePayload])
def update_my_profile(payload: UpdateProfileRequest, current_user: dict = Depends(get_current_firebase_user)) -> ApiResponse[ProfilePayload]:
    updated_profile = update_profile_by_uid(current_user["uid"], payload)
    return ApiResponse(success=True, message="Profile updated", data=updated_profile)
