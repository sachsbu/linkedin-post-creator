import asyncio
import time
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import httpx
from app.config import settings
from app.models.domain import Story
from app.sources.base import BaseSourceFetcher

class HackerNewsFetcher(BaseSourceFetcher):
    IOT_KEYWORDS = {
        "iot", "internet of things", "esp32", "esp8266", "raspberry pi",
        "arduino", "embedded", "smart home", "zigbee", "z-wave", "mqtt",
        "microcontroller", "sensors", "sensor", "firmware", "edge computing",
        "home assistant", "stm32", "risc-v", "matter protocol", "lora",
        "lorawan", "ble", "bluetooth low energy"
    }

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

    def _is_iot_story(self, title: str) -> bool:
        title_lower = title.lower()
        return any(kw in title_lower for kw in self.IOT_KEYWORDS)

    async def _fetch_item(self, client: httpx.AsyncClient, story_id: str) -> Optional[Dict[str, Any]]:
        try:
            item_url = f"{settings.HN_API_BASE}/item/{story_id}.json"
            resp = await client.get(item_url)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return None

    async def fetch_trending_stories(self, limit: int = 15) -> List[Story]:
        """
        Fetches trending stories with a focus on IoT-related news:
        ~10 out of 15 stories focused on IoT, and ~5 from general top HN stories.
        """
        target_iot_count = max(1, min(limit, round(limit * (10 / 15))))

        iot_stories: List[Story] = []
        general_stories: List[Story] = []
        seen_ids = set()

        async with httpx.AsyncClient(timeout=10.0) as client:
            # 1. Fetch IoT stories using Algolia HN Search API
            try:
                pop_url = "https://hn.algolia.com/api/v1/search?query=IoT&tags=story&hitsPerPage=30"
                rec_url = "https://hn.algolia.com/api/v1/search_by_date?query=IoT&tags=story&hitsPerPage=30"
                
                pop_resp, rec_resp = await asyncio.gather(
                    client.get(pop_url),
                    client.get(rec_url),
                    return_exceptions=True
                )

                pop_hits = pop_resp.json().get("hits", []) if isinstance(pop_resp, httpx.Response) and pop_resp.status_code == 200 else []
                rec_hits = rec_resp.json().get("hits", []) if isinstance(rec_resp, httpx.Response) and rec_resp.status_code == 200 else []

                for hit in pop_hits + rec_hits:
                    sid = str(hit.get("objectID", ""))
                    if not sid or sid in seen_ids:
                        continue
                    
                    title = hit.get("title", "").strip()
                    if not title:
                        continue

                    seen_ids.add(sid)
                    url = hit.get("url") or f"https://news.ycombinator.com/item?id={sid}"
                    score = hit.get("points") or 0
                    comments_count = hit.get("num_comments") or 0
                    hn_url = f"https://news.ycombinator.com/item?id={sid}"
                    timestamp = hit.get("created_at_i") or int(time.time())
                    published_at = datetime.fromtimestamp(timestamp, tz=timezone.utc)
                    author = hit.get("author", "anonymous")

                    rank_score = self.calculate_rank_score(score, comments_count, timestamp)

                    iot_stories.append(
                        Story(
                            id=sid,
                            title=title,
                            url=url,
                            hn_url=hn_url,
                            author=author,
                            score=score,
                            comments_count=comments_count,
                            published_at=published_at,
                            rank_score=rank_score,
                            source_name="Hacker News (IoT)",
                        )
                    )
            except Exception:
                pass

            # 2. Fetch General Top Stories concurrently from official Firebase HN API
            try:
                top_stories_url = f"{settings.HN_API_BASE}/topstories.json"
                response = await client.get(top_stories_url)
                if response.status_code == 200:
                    candidate_ids = [str(sid) for sid in response.json()[: limit * 2] if str(sid) not in seen_ids]
                    items_data = await asyncio.gather(*[self._fetch_item(client, sid) for sid in candidate_ids])

                    for sid, data in zip(candidate_ids, items_data):
                        if not data or data.get("type") != "story" or data.get("deleted") or data.get("dead"):
                            continue

                        title = data.get("title", "")
                        url = data.get("url", f"https://news.ycombinator.com/item?id={sid}")
                        score = data.get("score", 0)
                        comments_count = data.get("descendants", 0)
                        hn_url = f"https://news.ycombinator.com/item?id={sid}"
                        timestamp = data.get("time", int(time.time()))
                        published_at = datetime.fromtimestamp(timestamp, tz=timezone.utc)
                        author = data.get("by", "anonymous")

                        rank_score = self.calculate_rank_score(score, comments_count, timestamp)
                        is_iot = self._is_iot_story(title)
                        source_name = "Hacker News (IoT)" if is_iot else self.name

                        story_obj = Story(
                            id=sid,
                            title=title,
                            url=url,
                            hn_url=hn_url,
                            author=author,
                            score=score,
                            comments_count=comments_count,
                            published_at=published_at,
                            rank_score=rank_score,
                            source_name=source_name,
                        )

                        seen_ids.add(sid)
                        if is_iot:
                            iot_stories.append(story_obj)
                        else:
                            general_stories.append(story_obj)
            except Exception:
                pass

            # Sort pools by rank_score descending
            iot_stories.sort(key=lambda s: s.rank_score, reverse=True)
            general_stories.sort(key=lambda s: s.rank_score, reverse=True)

            # Select top IoT stories and General stories
            selected_iot = iot_stories[:target_iot_count]
            remaining_slots = limit - len(selected_iot)
            selected_general = general_stories[:remaining_slots]

            final_stories = selected_iot + selected_general
            if len(final_stories) < limit:
                leftover_iot = iot_stories[target_iot_count:]
                final_stories.extend(leftover_iot[: limit - len(final_stories)])

            return final_stories[:limit]


