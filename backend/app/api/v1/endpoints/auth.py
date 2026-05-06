import logging

from fastapi import APIRouter, HTTPException, status

from app.schemas.auth import AuthPayload, FirebaseAuthRequest, LoginRequest, SignupRequest
from app.schemas.common import ApiResponse
from app.services.firebase_admin_service import verify_firebase_token
from app.services.user_service import get_or_create_user_from_firebase

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/signup", response_model=ApiResponse[AuthPayload])
def signup(_: SignupRequest) -> ApiResponse[AuthPayload]:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Direct API signup is disabled. Use Firebase Authentication from the frontend.",
    )


@router.post("/login", response_model=ApiResponse[AuthPayload])
def login(_: LoginRequest) -> ApiResponse[AuthPayload]:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Direct API login is disabled. Use Firebase Authentication from the frontend.",
    )


@router.post("/firebase", response_model=ApiResponse[AuthPayload])
def firebase_auth(payload: FirebaseAuthRequest) -> ApiResponse[AuthPayload]:
    try:
        decoded_token = verify_firebase_token(payload.id_token)
        auth_payload = get_or_create_user_from_firebase(decoded_token)
        return ApiResponse(success=True, message="Firebase authentication successful", data=auth_payload)
    except Exception as exc:
        logger.exception("Firebase auth exchange failed")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed") from exc
