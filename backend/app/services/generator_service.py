import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.domain import Story, ArticleSummary, PostResponse
from app.models.db_models import PostDB
from app.sources.registry import source_registry
from app.scraper.article_scraper import ArticleScraper
from app.scraper.image_service import ImageService
from app.ai.factory import AIFactory
from app.services.exporter import ArtifactExporter

class GeneratorService:
    @staticmethod
    def _slugify(text: str) -> str:
        slug = re.sub(r"[^\w\s-]", "", text.lower())
        return re.sub(r"[-\s]+", "-", slug).strip("-")[:40]

    @classmethod
    async def generate_post_pipeline(
        self,
        db: AsyncSession,
        story_id: Optional[str] = None,
        source_name: str = "Hacker News",
        tone: str = "professional",
        provider_name: Optional[str] = None,
        model_name: Optional[str] = None,
        custom_title: Optional[str] = None,
        custom_url: Optional[str] = None,
        generate_image: bool = False
    ) -> PostResponse:
        # 1. Resolve target story or create custom self story
        if custom_title or source_name.lower() in ["self", "custom"]:
            title = (custom_title or "").strip() or "Self-authored Post"
            url = (custom_url or "").strip() or "self"
            target_story = Story(
                id=f"custom_{int(datetime.utcnow().timestamp())}",
                title=title,
                url=url,
                hn_url=url,
                author="Self",
                score=0,
                comments_count=0,
                source_name="self"
            )
        else:
            if story_id and story_id.startswith("cnet_"):
                source_name = "cnet"

            fetcher = source_registry.get(source_name)
            trending_stories = await fetcher.fetch_trending_stories(limit=25)

            target_story: Optional[Story] = None
            if story_id:
                for s in trending_stories:
                    if s.id == story_id:
                        target_story = s
                        break

            if not target_story:
                if not trending_stories:
                    raise RuntimeError("Failed to fetch stories from news source.")
                target_story = trending_stories[0]  # Pick top story

        # 2. Scrape article content & OpenGraph metadata
        if target_story.url == "self" or not target_story.url.startswith(("http://", "https://")):
            scraped_data = {"content": target_story.title, "og_image": None, "site_name": "self"}
        else:
            scraped_data = await ArticleScraper.scrape(target_story.url)

        content = scraped_data.get("content", "") or target_story.title
        og_image_url = scraped_data.get("og_image")
        publication = scraped_data.get("site_name") or target_story.source_name

        # 3. Instantiate AI Provider
        llm = AIFactory.get_provider(provider_name=provider_name, model=model_name)

        # 4. Generate AI Summary & LinkedIn Post Caption
        summary: ArticleSummary = await llm.summarize_article(
            title=target_story.title,
            content=content,
            source_url=target_story.url
        )

        post_data = await llm.generate_linkedin_post(
            title=target_story.title,
            summary=summary,
            source_url=target_story.url,
            tone=tone
        )

        caption = post_data["caption"]
        hashtags = post_data["hashtags"]
        word_count = post_data["word_count"]

        # 5. Resolve/Generate Image & Create Output Artifact Directory
        timestamp_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        folder_slug = f"{timestamp_str}_{self._slugify(target_story.title)}"
        output_dir = settings.OUTPUT_FOLDER / folder_slug

        # Use real OG image if available; if missing/invalid, generate synthetic image card
        image_path, image_type = await ImageService.resolve_or_generate_image(
            og_image_url=og_image_url,
            title=target_story.title,
            publication=publication,
            output_dir=output_dir,
            generate_custom_fallback=True
        )

        # 6. Write post.md, post.txt, metadata.json artifacts
        ArtifactExporter.export_all(
            output_dir=output_dir,
            story=target_story,
            summary=summary,
            caption=caption,
            hashtags=hashtags,
            image_path=image_path,
            image_type=image_type,
            tone=tone,
            model_used=llm.provider_name
        )

        # 7. Persist record to SQLite DB
        db_post = PostDB(
            story_id=target_story.id,
            source_name=target_story.source_name,
            title=target_story.title,
            source_url=target_story.url,
            hn_url=target_story.hn_url,
            author=target_story.author,
            score=target_story.score,
            comments_count=target_story.comments_count,
            summary_what=summary.what_happened,
            summary_why=summary.why_it_matters,
            summary_impact=summary.impact,
            summary_takeaway=summary.key_takeaway,
            linkedin_caption=caption,
            hashtags=",".join(hashtags),
            word_count=word_count,
            tone=tone,
            image_path=str(image_path) if image_path else "",
            image_type=image_type,
            output_folder=str(output_dir),
            model_used=llm.provider_name,
            created_at=datetime.utcnow()
        )
        db.add(db_post)
        await db.commit()
        await db.refresh(db_post)

        return PostResponse(
            id=db_post.id,
            story_id=target_story.id,
            source_name=target_story.source_name,
            title=target_story.title,
            source_url=target_story.url,
            hn_url=target_story.hn_url,
            author=target_story.author,
            score=target_story.score,
            comments_count=target_story.comments_count,
            summary=summary,
            linkedin_caption=caption,
            hashtags=hashtags,
            word_count=word_count,
            tone=tone,
            image_path=str(image_path),
            image_type=image_type,
            output_folder=str(output_dir),
            model_used=llm.provider_name,
            created_at=db_post.created_at
        )
