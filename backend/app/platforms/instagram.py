from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.platforms.base import SocialPlatformGenerator
from app.services.media_validation_service import MediaValidationService
from app.ai.factory import AIFactory
from app.models.domain import InstagramPostResponse, MediaValidationResult
from app.models.db_models import PostDB

class InstagramGenerator(SocialPlatformGenerator):
    @property
    def platform_name(self) -> str:
        return "instagram"

    async def validate_input(
        self,
        prompt: str,
        media_path: Optional[str] = None,
        media_type: str = "image",
        **kwargs
    ) -> Dict[str, Any]:
        errors = []
        warnings = []

        if not prompt or not prompt.strip():
            errors.append("Content prompt is required.")

        media_val_result: Optional[MediaValidationResult] = None
        if media_path:
            full_path = Path(media_path)
            if not full_path.is_absolute():
                uploads_path = settings.OUTPUT_FOLDER / "uploads" / media_path
                output_path = settings.OUTPUT_FOLDER / media_path
                if uploads_path.exists():
                    full_path = uploads_path
                elif output_path.exists():
                    full_path = output_path
                else:
                    full_path = uploads_path

            if full_path.exists():
                if media_type == "video":
                    media_val_result = MediaValidationService.validate_video(full_path, full_path.name)
                else:
                    media_val_result = MediaValidationService.validate_image(full_path, full_path.name)

                if media_val_result:
                    errors.extend(media_val_result.errors)
                    warnings.extend(media_val_result.warnings)
            else:
                warnings.append(f"Media file '{media_path}' path was not found on server disk.")

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "media_validation": media_val_result
        }

    async def generate_post(
        self,
        db: AsyncSession,
        prompt: str,
        media_path: Optional[str] = None,
        media_type: str = "image",
        provider_name: Optional[str] = None,
        model_name: Optional[str] = None,
        **kwargs
    ) -> InstagramPostResponse:
        # 1. Validate inputs & media
        validation_res = await self.validate_input(
            prompt=prompt,
            media_path=media_path,
            media_type=media_type
        )
        if not validation_res["is_valid"]:
            raise ValueError(f"Input validation failed: {', '.join(validation_res['errors'])}")

        # 2. Instantiate LLM provider
        llm = AIFactory.get_provider(provider_name=provider_name, model=model_name)

        # 3. Generate Instagram caption & hashtags via LLM
        res = await llm.generate_instagram_post(prompt=prompt, media_type=media_type)

        caption = res.get("caption", "")
        hashtags = res.get("hashtags", [])

        # 4. Save to Database (with graceful fallback)
        post_id = None
        created_at = datetime.utcnow()
        try:
            db_post = PostDB(
                platform="instagram",
                story_id=f"insta_{int(datetime.utcnow().timestamp())}",
                source_name="Instagram",
                title=prompt[:60],
                source_url="",
                hn_url="",
                author="User",
                score=0,
                comments_count=0,
                summary_what=prompt,
                summary_why="",
                summary_impact="",
                summary_takeaway="",
                linkedin_caption=caption,
                hashtags=",".join(hashtags),
                word_count=len(caption.split()),
                tone="friendly",
                image_path=media_path or "",
                image_type=media_type,
                output_folder=str(settings.OUTPUT_FOLDER),
                model_used=llm.provider_name,
                created_at=created_at
            )
            db.add(db_post)
            await db.commit()
            await db.refresh(db_post)
            post_id = db_post.id
            created_at = db_post.created_at
        except Exception as db_err:
            import logging
            logging.getLogger(__name__).warning(f"Failed to persist Instagram post to database: {db_err}")
            await db.rollback()

        return InstagramPostResponse(
            id=post_id,
            platform="instagram",
            prompt=prompt,
            caption=caption,
            hashtags=hashtags,
            media_path=media_path,
            media_type=media_type,
            warnings=validation_res.get("warnings", []),
            model_used=llm.provider_name,
            created_at=created_at
        )
