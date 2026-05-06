from fastapi import APIRouter, Depends

from app.api.deps import get_current_firebase_user
from app.schemas.common import ApiResponse
from app.schemas.neo4j import Neo4jStatusPayload, Neo4jSyncPayload
from app.services.graph_projection_service import get_neo4j_status, sync_user_graph

router = APIRouter()


@router.get("/status", response_model=ApiResponse[Neo4jStatusPayload])
def neo4j_status(_: dict = Depends(get_current_firebase_user)) -> ApiResponse[Neo4jStatusPayload]:
    return ApiResponse(success=True, data=get_neo4j_status())


@router.post("/sync", response_model=ApiResponse[Neo4jSyncPayload])
def neo4j_sync(current_user: dict = Depends(get_current_firebase_user)) -> ApiResponse[Neo4jSyncPayload]:
    payload = sync_user_graph(current_user["uid"])
    return ApiResponse(success=True, message="Neo4j graph sync completed", data=payload)
