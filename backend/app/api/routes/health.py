from fastapi import APIRouter

from app.core.config import get_settings


router = APIRouter(tags=["system"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    settings = get_settings()
    return {
        "service": settings.app_name,
        "status": "ok",
        "version": settings.version,
    }
