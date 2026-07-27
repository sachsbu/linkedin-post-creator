from fastapi import APIRouter
from app.config import settings

router = APIRouter(prefix="/api/health", tags=["Health"])

@router.get("")
async def health_check():
    return {
        "status": "online",
        "app_name": settings.APP_NAME,
        "default_provider": settings.LLM_PROVIDER,
        "output_folder": str(settings.OUTPUT_FOLDER.resolve())
    }
