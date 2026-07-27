import time
from datetime import datetime, timezone
from typing import List, Dict, Any
import httpx
from app.config import settings
from app.models.domain import Story
from app.sources.base import BaseSourceFetcher

class HackerNewsFetcher(BaseSourceFetcher):
    @property
    def name(self) -> str:
        return "Hacker News"

    def calculate_rank_score(self, score: int, comments: int, timestamp: int) -> float:
        """
        Calculates ranking score balancing popularity (score, comments) and recency decay.
        Score = (Score + Comments * 1.5) / (Age_in_hours + 2)^1.8
        """
        now = time.time()
        age_hours = max((now - timestamp) / 3600.0, 0.1)
        base_points = score + (comments * 1.5)
        decay = (age_hours + 2.0) ** 1.8
        return base_points / decay

    async def fetch_trending_stories(self, limit: int = 20) -> List[Story]:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # 1. Fetch top story IDs
            top_stories_url = f"{settings.HN_API_BASE}/topstories.json"
            response = await client.get(top_stories_url)
            response.raise_for_status()
            story_ids = response.json()[: limit * 2]  # Fetch candidates

            stories: List[Story] = []
            for story_id in story_ids:
                try:
                    item_url = f"{settings.HN_API_BASE}/item/{story_id}.json"
                    item_resp = await client.get(item_url)
                    if item_resp.status_code != 200:
                        continue
                    data: Dict[Any, Any] = item_resp.json()
                    
                    if not data or data.get("type") != "story" or data.get("deleted") or data.get("dead"):
                        continue

                    title = data.get("title", "")
                    url = data.get("url", f"https://news.ycombinator.com/item?id={story_id}")
                    score = data.get("score", 0)
                    comments_count = data.get("descendants", 0)
                    hn_url = f"https://news.ycombinator.com/item?id={story_id}"
                    timestamp = data.get("time", int(time.time()))
                    published_at = datetime.fromtimestamp(timestamp, tz=timezone.utc)
                    author = data.get("by", "anonymous")

                    rank_score = self.calculate_rank_score(score, comments_count, timestamp)

                    stories.append(
                        Story(
                            id=str(story_id),
                            title=title,
                            url=url,
                            hn_url=hn_url,
                            author=author,
                            score=score,
                            comments_count=comments_count,
                            published_at=published_at,
                            rank_score=rank_score,
                            source_name=self.name,
                        )
                    )
                except Exception:
                    continue

            # Sort by rank_score descending
            stories.sort(key=lambda s: s.rank_score, reverse=True)
            return stories[:limit]
