from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "DocuRAG AgentOps Backend"
    version: str = "0.1.0"
    environment: str = "local"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="DOCURAG_",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
