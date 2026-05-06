from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Platform API"
    app_version: str = "0.1.0"
    api_v1_prefix: str = "/api/v1"
    allowed_origins: str = (
        "http://localhost:5173,"
        "http://localhost:5174,"
        "http://localhost:5175,"
        "http://127.0.0.1:5173,"
        "http://127.0.0.1:5174,"
        "http://127.0.0.1:5175"
    )
    mongodb_uri: str = "mongodb+srv://<username>:<password>@<cluster-url>/"
    mongodb_database: str = "ai_platform"
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_username: str = "neo4j"
    neo4j_password: str = "password"
    secret_key: str = "change-this-before-production"
    openalex_api_key: str | None = None
    openalex_base_url: str = "https://api.openalex.org"
    usajobs_api_key: str | None = None
    usajobs_user_agent: str | None = None
    usajobs_host: str = "data.usajobs.gov"
    onet_api_key: str | None = None
    onet_base_url: str = "https://services.onetcenter.org/ws/"
    firebase_project_id: str | None = None
    firebase_credentials_path: str | None = None
    firebase_service_account_json: str | None = None
    firebase_clock_skew_seconds: int = 10
    data_dir: str = "data"

    @property
    def cors_allowed_origins(self) -> list[str]:
        return [origin.strip().rstrip("/") for origin in self.allowed_origins.split(",") if origin.strip()]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
