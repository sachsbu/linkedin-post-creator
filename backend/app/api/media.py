import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.config import settings
from app.services.media_validation_service import MediaValidationService
from app.models.domain import MediaValidationResult

router = APIRouter(prefix="/api/media", tags=["Media"])

UPLOADS_DIR = settings.OUTPUT_FOLDER / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/upload", response_model=MediaValidationResult)
async def upload_media(file: UploadFile = File(...)):
    """
    Uploads and validates image or video media file for Instagram posts.
    Supports JPEG, PNG, WEBP, MP4, MOV.
    """
    try:
        filename = file.filename or "uploaded_media"
        file_path = UPLOADS_DIR / filename
        
        # Save file to uploads folder
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        content_type = file.content_type or ""
        ext = Path(filename).suffix.lower()

        if ext in [".mp4", ".mov"] or "video" in content_type:
            val_result = MediaValidationService.validate_video(
                file_path=file_path,
                filename=filename,
                mime_type=content_type
            )
        else:
            val_result = MediaValidationService.validate_image(
                file_path=file_path,
                filename=filename,
                mime_type=content_type
            )

        if not val_result.is_valid:
            # Keep file if warnings only, but log errors
            pass

        return val_result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Media upload error: {str(e)}")
