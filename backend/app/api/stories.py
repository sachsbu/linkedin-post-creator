from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException
from app.models.domain import Story
from app.sources.registry import source_registry

router = APIRouter(prefix="/api/stories", tags=["Stories"])

@router.get("/trending", response_model=List[Story])
async def get_trending_stories(
    source: str = Query("hacker_news", description="Source name"),
    limit: int = Query(15, ge=1, le=50)
):
    """
    Fetches and ranks trending stories from the specified news source.
    """
    try:
        fetcher = source_registry.get(source)
        stories = await fetcher.fetch_trending_stories(limit=limit)
        return stories
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch trending stories: {str(e)}")

@router.get("/sources")
async def list_sources():
    """Returns list of registered news sources."""
    return source_registry.list_sources()
