from fastapi import APIRouter, Depends

from app.api.deps import get_current_firebase_user
from app.schemas.common import ApiResponse
from app.schemas.dashboard import CourseItem, PaperItem
from app.schemas.progress import CompletionRemoveRequest, UserProgressPayload
from app.services.progress_service import (
    complete_course_by_uid,
    complete_paper_by_uid,
    get_progress_by_uid,
    uncomplete_course_by_uid,
    uncomplete_paper_by_uid,
)

router = APIRouter()


@router.get("", response_model=ApiResponse[UserProgressPayload])
def get_progress(current_user: dict = Depends(get_current_firebase_user)) -> ApiResponse[UserProgressPayload]:
    return ApiResponse(success=True, data=get_progress_by_uid(current_user["uid"]))


@router.post("/courses/complete", response_model=ApiResponse[UserProgressPayload])
def complete_course(payload: CourseItem, current_user: dict = Depends(get_current_firebase_user)) -> ApiResponse[UserProgressPayload]:
    return ApiResponse(success=True, message="Course marked as completed", data=complete_course_by_uid(current_user["uid"], payload))


@router.post("/courses/remove", response_model=ApiResponse[UserProgressPayload])
def remove_completed_course(payload: CompletionRemoveRequest, current_user: dict = Depends(get_current_firebase_user)) -> ApiResponse[UserProgressPayload]:
    return ApiResponse(success=True, message="Course moved back to active", data=uncomplete_course_by_uid(current_user["uid"], payload.item_id))


@router.post("/papers/complete", response_model=ApiResponse[UserProgressPayload])
def complete_paper(payload: PaperItem, current_user: dict = Depends(get_current_firebase_user)) -> ApiResponse[UserProgressPayload]:
    return ApiResponse(success=True, message="Paper marked as read", data=complete_paper_by_uid(current_user["uid"], payload))


@router.post("/papers/remove", response_model=ApiResponse[UserProgressPayload])
def remove_completed_paper(payload: CompletionRemoveRequest, current_user: dict = Depends(get_current_firebase_user)) -> ApiResponse[UserProgressPayload]:
    return ApiResponse(success=True, message="Paper moved back to active", data=uncomplete_paper_by_uid(current_user["uid"], payload.item_id))
