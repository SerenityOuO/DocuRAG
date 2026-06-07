from fastapi import APIRouter

from app.core.config import get_settings
from app.services.redis_runtime import create_redis_runtime


router = APIRouter(tags=["system"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    settings = get_settings()
    redis_health = create_redis_runtime(settings).health()
    body = {
        "service": settings.app_name,
        "status": "ok",
        "version": settings.version,
        "redis": redis_health.status,
    }
    if redis_health.detail:
        body["redis_detail"] = redis_health.detail

    return body
