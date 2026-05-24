from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def default_data_dir() -> Path:
    current_dir = Path.cwd()

    if (current_dir / "backend").is_dir() and (current_dir / "frontend").is_dir():
        return current_dir / "data"

    if current_dir.name == "backend" and (current_dir / "app").is_dir():
        return current_dir.parent / "data"

    return current_dir / "data"


class Settings(BaseSettings):
    app_name: str = "DocuRAG AgentOps Backend"
    version: str = "0.24.0"
    environment: str = "local"
    data_dir: Path = Field(default_factory=default_data_dir)
    ocr_provider: str = "paddleocr"
    ocr_language: str = "ch"
    ocr_version: str = "PP-OCRv4"
    ocr_det_model_name: str = "PP-OCRv4_mobile_det"
    ocr_rec_model_name: str = "PP-OCRv4_mobile_rec"
    ocr_cls_model_name: str = "ch_ppocr_mobile_v2.0_cls"
    ocr_det_model_dir: str | None = None
    ocr_rec_model_dir: str | None = None
    ocr_cls_model_dir: str | None = None
    ocr_use_angle_cls: bool = False
    ocr_det_limit_side_len: int = 960
    ocr_rec_batch_num: int = 6
    llm_provider: str | None = "ollama"
    llm_base_url: str = "http://127.0.0.1:11434"
    llm_model: str = "qwen3.5:4b"
    llm_timeout_seconds: float = 30.0
    embedding_provider: str | None = None
    embedding_base_url: str = "http://127.0.0.1:11434"
    embedding_model: str = "qwen3-embedding:0.6b"
    embedding_timeout_seconds: float = 30.0
    qdrant_url: str = "http://127.0.0.1:6333"
    qdrant_collection: str = "docurag_chunks_v1"
    qdrant_vector_size: int = 1024
    qdrant_timeout_seconds: float = 10.0
    rag_retrieval_provider: str = "keyword"
    rerank_provider: str | None = None
    rerank_model: str = "BAAI/bge-reranker-base"
    rerank_top_k: int = 5
    rerank_timeout_seconds: float = 30.0
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
