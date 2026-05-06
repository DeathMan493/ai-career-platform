from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.database.validators import ensure_database_guards


def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Backend scaffold for the AI Platform knowledge-graph recommendation system.",
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @application.get("/health", tags=["health"])
    def health_check() -> dict[str, str]:
        return {"status": "ok"}

    @application.on_event("startup")
    def startup_tasks() -> None:
        ensure_database_guards()

    application.include_router(api_router, prefix=settings.api_v1_prefix)
    return application


app = create_application()
