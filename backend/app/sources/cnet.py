import time
import hashlib
import logging
from datetime import datetime, timezone
from typing import List
import httpx
from bs4 import BeautifulSoup
from app.models.domain import Story
from app.sources.base import BaseSourceFetcher

logger = logging.getLogger(__name__)

class CNETFetcher(BaseSourceFetcher):
    @property
    def name(self) -> str:
        return "CNET"

    async def fetch_trending_stories(self, limit: int = 20) -> List[Story]:
        url = "https://www.cnet.com/tech/"
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        }

        stories: List[Story] = []
        seen_urls = set()

        try:
            async with httpx.AsyncClient(timeout=12.0, follow_redirects=True) as client:
                resp = await client.get(url, headers=headers)
                if resp.status_code != 200:
                    logger.warning(f"CNET fetch failed with status {resp.status_code}")
                    return stories

                soup = BeautifulSoup(resp.text, "html.parser")
                rank_position = 1

                for a_tag in soup.find_all("a"):
                    href = a_tag.get("href", "")
                    title = a_tag.get_text().strip()

                    # Filter relevant CNET article links
                    if not href or not title or len(title) < 22:
                        continue

                    if not ("/tech/" in href or "/news/" in href or "/services-and-software/" in href):
                        continue

                    full_url = href if href.startswith("http") else f"https://www.cnet.com{href}"

                    # Exclude category hub pages
                    if full_url.rstrip("/") in {
                        "https://www.cnet.com/tech",
                        "https://www.cnet.com/tech/services-and-software",
                        "https://www.cnet.com/tech/mobile",
                        "https://www.cnet.com/tech/home-entertainment",
                        "https://www.cnet.com/tech/computing"
                    }:
                        continue

                    if full_url in seen_urls:
                        continue

                    seen_urls.add(full_url)

                    # Deterministic ID for CNET story
                    story_id = f"cnet_{hashlib.md5(full_url.encode()).hexdigest()[:10]}"
                    
                    # Score decay based on page position
                    rank_score = max(100.0 - (rank_position * 2.5), 10.0)

                    stories.append(
                        Story(
                            id=story_id,
                            title=title,
                            url=full_url,
                            hn_url=full_url,
                            author="CNET Tech",
                            score=150 - rank_position,
                            comments_count=25,
                            published_at=datetime.now(timezone.utc),
                            rank_score=rank_score,
                            source_name=self.name,
                        )
                    )

                    rank_position += 1
                    if len(stories) >= limit:
                        break

        except Exception as e:
            logger.error(f"Error fetching CNET stories: {e}")

        return stories
