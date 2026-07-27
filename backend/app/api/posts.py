from typing import List, Optional
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.database import get_db
from app.models.domain import GeneratePostRequest, PostResponse, ArticleSummary
from app.models.db_models import PostDB
from app.services.generator_service import GeneratorService
from app.services.exporter import ArtifactExporter

router = APIRouter(prefix="/api/posts", tags=["Posts"])

@router.post("/generate", response_model=PostResponse)
async def generate_post(
    req: GeneratePostRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generates a high-quality LinkedIn post for the top story or specified story ID.
    """
    try:
        res = await GeneratorService.generate_post_pipeline(
            db=db,
            story_id=req.story_id,
            tone=req.tone,
            provider_name=req.provider,
            model_name=req.model
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Post generation error: {str(e)}")

@router.get("/history", response_model=List[PostResponse])
async def get_post_history(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns history of generated LinkedIn posts.
    """
    stmt = select(PostDB).order_by(desc(PostDB.created_at)).limit(limit)
    result = await db.execute(stmt)
    posts_db = result.scalars().all()

    responses = []
    for p in posts_db:
        summary = ArticleSummary(
            what_happened=p.summary_what or "",
            why_it_matters=p.summary_why or "",
            impact=p.summary_impact or "",
            key_takeaway=p.summary_takeaway or ""
        )
        hashtags = [h.strip() for h in (p.hashtags or "").split(",") if h.strip()]
        responses.append(
            PostResponse(
                id=p.id,
                story_id=p.story_id,
                source_name=p.source_name,
                title=p.title,
                source_url=p.source_url,
                hn_url=p.hn_url,
                author=p.author,
                score=p.score,
                comments_count=p.comments_count,
                summary=summary,
                linkedin_caption=p.linkedin_caption,
                hashtags=hashtags,
                word_count=p.word_count,
                tone=p.tone,
                image_path=p.image_path,
                image_type=p.image_type,
                output_folder=p.output_folder,
                model_used=p.model_used,
                created_at=p.created_at
            )
        )
    return responses

@router.get("/{post_id}/export")
async def export_post(
    post_id: int,
    format: str = Query("md", enum=["md", "txt", "json", "html"]),
    db: AsyncSession = Depends(get_db)
):
    """
    Exports post artifact file in Markdown, plain text, JSON, or HTML.
    """
    stmt = select(PostDB).where(PostDB.id == post_id)
    res = await db.execute(stmt)
    post = res.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    folder = Path(post.output_folder)
    
    if format == "md":
        file_path = folder / "post.md"
        if file_path.exists():
            return FileResponse(file_path, media_type="text/markdown", filename=f"post_{post_id}.md")
    elif format == "txt":
        file_path = folder / "post.txt"
        if file_path.exists():
            return FileResponse(file_path, media_type="text/plain", filename=f"post_{post_id}.txt")
    elif format == "json":
        file_path = folder / "metadata.json"
        if file_path.exists():
            return FileResponse(file_path, media_type="application/json", filename=f"metadata_{post_id}.json")
    elif format == "html":
        hashtags = [h.strip() for h in (post.hashtags or "").split(",") if h.strip()]
        img_filename = Path(post.image_path).name
        html_code = ArtifactExporter.to_html(
            title=post.title,
            caption=post.linkedin_caption,
            hashtags=hashtags,
            source_url=post.source_url,
            img_name=img_filename
        )
        return HTMLResponse(content=html_code)

    raise HTTPException(status_code=404, detail=f"Export file for format '{format}' not found")
