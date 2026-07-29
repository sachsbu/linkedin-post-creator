from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.platforms.base import SocialPlatformGenerator
from app.services.generator_service import GeneratorService

class LinkedInGenerator(SocialPlatformGenerator):
    @property
    def platform_name(self) -> str:
        return "linkedin"

    async def validate_input(self, tone: str = "professional", **kwargs) -> Dict[str, Any]:
        valid_tones = ["professional", "founder", "developer", "investor"]
        if tone.lower() not in valid_tones:
            return {"is_valid": False, "errors": [f"Invalid tone '{tone}'. Allowed: {valid_tones}"]}
        return {"is_valid": True, "errors": []}

    async def generate_post(
        self,
        db: AsyncSession,
        story_id: Optional[str] = None,
        source_name: str = "Hacker News",
        tone: str = "professional",
        provider_name: Optional[str] = None,
        model_name: Optional[str] = None,
        custom_title: Optional[str] = None,
        custom_url: Optional[str] = None,
        generate_image: bool = False,
        **kwargs
    ) -> Any:
        return await GeneratorService.generate_post_pipeline(
            db=db,
            story_id=story_id,
            source_name=source_name,
            tone=tone,
            provider_name=provider_name,
            model_name=model_name,
            custom_title=custom_title,
            custom_url=custom_url,
            generate_image=generate_image
        )
