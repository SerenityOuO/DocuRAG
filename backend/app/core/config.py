from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    app_name: str = "DocuRAG AgentOps"
    app_version: str = "0.1.0"
    database_url: str = "postgresql+psycopg://docurag:docurag@localhost:5432/docurag"
    redis_url: str = "redis://localhost:6379/0"
    qdrant_url: str = "http://localhost:6333"
    nats_url: str = "nats://localhost:4222"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
