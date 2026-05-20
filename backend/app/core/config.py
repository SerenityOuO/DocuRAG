from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "DocuRAG AgentOps Backend"
    version: str = "0.2.0"
    environment: str = "local"
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="DOCURAG_",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
