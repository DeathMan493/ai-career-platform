from __future__ import annotations

from fastapi import Header, HTTPException, status

from app.schemas.common import PaginatedPayload, PaginationMeta
from app.services.firebase_admin_service import verify_firebase_token


async def get_current_firebase_user(authorization: str | None = Header(default=None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    id_token = authorization.split(" ", 1)[1].strip()
    if not id_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    try:
        return verify_firebase_token(id_token)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized") from exc


def paginate_items(items: list, page: int, limit: int) -> PaginatedPayload:
    offset = (page - 1) * limit
    page_items = items[offset : offset + limit]

    return PaginatedPayload(
        items=page_items,
        pagination=PaginationMeta(
            page=page,
            limit=limit,
            returned=len(page_items),
            has_next=len(items) > offset + limit,
            has_previous=page > 1,
        ),
    )
