from fastapi import APIRouter, Depends

from app.api.deps import get_current_firebase_user
from app.api.v1.endpoints import auth, courses, dashboard, evaluation, graph, neo4j, papers, profile, progress, skill_gap, skills

api_router = APIRouter()
protected_dependencies = [Depends(get_current_firebase_user)]

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(profile.router, prefix="/profile", tags=["profile"], dependencies=protected_dependencies)
api_router.include_router(progress.router, prefix="/progress", tags=["progress"], dependencies=protected_dependencies)
api_router.include_router(neo4j.router, prefix="/neo4j", tags=["neo4j"], dependencies=protected_dependencies)
api_router.include_router(skills.router, prefix="/skills", tags=["skills"], dependencies=protected_dependencies)
api_router.include_router(courses.router, prefix="/courses", tags=["courses"], dependencies=protected_dependencies)
api_router.include_router(papers.router, prefix="/papers", tags=["papers"], dependencies=protected_dependencies)
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"], dependencies=protected_dependencies)
api_router.include_router(skill_gap.router, prefix="/skill-gap", tags=["skill-gap"], dependencies=protected_dependencies)
api_router.include_router(graph.router, prefix="/graph", tags=["graph"], dependencies=protected_dependencies)
api_router.include_router(evaluation.router, prefix="/evaluation", tags=["evaluation"], dependencies=protected_dependencies)
