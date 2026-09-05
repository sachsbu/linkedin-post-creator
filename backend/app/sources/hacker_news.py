import asyncio
import re
import time
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import httpx
from app.config import settings
from app.models.domain import Story
from app.sources.base import BaseSourceFetcher

class HackerNewsFetcher(BaseSourceFetcher):
    IOT_PATTERNS = [
        r"\biot\b",
        r"\biiot\b",
        r"\binternet of things\b",
        r"\bsensors?\b",
        r"\bsensing\b",
        r"\btelemetry\b",
        r"\besp32[s]?\b",
        r"\besp8266[s]?\b",
        r"\besp-idf\b",
        r"\braspberry pi[s]?\b",
        r"\brp2040[s]?\b",
        r"\brp2350[s]?\b",
        r"\barduino[s]?\b",
        r"\bmqtt\b",
        r"\bzigbee\b",
        r"\bz-?wave\b",
        r"\blorawan?\b",
        r"\blora\b",
        r"\bble\b",
        r"\bbluetooth low energy\b",
        r"\bmatter (?:protocol|over thread|standard|device[s]?)\b",
        r"\bscada\b",
        r"\brisc-v\b",
        r"\bstm32[s]?\b",
        r"\bmicrocontrollers?\b",
        r"\bembedded (?:systems?|linux|firmware|hardware|devices?|engineering|software|rust|c\+\+|c)\b",
        r"\bfirmware\b",
        r"\bedge (?:computing|ai|devices?|gateways?)\b",
        r"\bsmart home\b",
        r"\bhome assistant\b",
        r"\b(?:condition|remote|cloud|sensor) monitoring\b",
        r"\bindustrial (?:iot|automation|telemetry)\b",
        r"\bconnected devices?\b",
        r"\baccelerometer[s]?\b",
        r"\blidar[s]?\b",
        r"\btransducers?\b",
        r"\bactuators?\b",
    ]
    IOT_REGEX = re.compile("|".join(IOT_PATTERNS), re.IGNORECASE)

    # Keywords that indicate high relevance to cloud sensor monitoring & telemetry (JediSense focus)
    SENSOR_MONITORING_BOOST_REGEX = re.compile(
        r"\b(sensors?|sensing|telemetry|condition monitoring|remote monitoring|cloud monitoring|sensor monitoring|scada|iiot|industrial iot|predictive maintenance)\b",
        re.IGNORECASE,
    )

    @property
    def name(self) -> str:
        return "Hacker News"

    def calculate_rank_score(
        self, score: int, comments: int, timestamp: int, is_sensor_focused: bool = False
    ) -> float:
        """
        Calculates ranking score balancing popularity (score, comments) and recency decay.
        Score = (Score + Comments * 1.5) / (Age_in_hours + 2)^1.8
        Stories focused specifically on sensors, telemetry, and monitoring receive a 1.35x relevance boost.
        """
        now = time.time()
        age_hours = max((now - timestamp) / 3600.0, 0.1)
        base_points = score + (comments * 1.5)
        decay = (age_hours + 2.0) ** 1.8
        rank = base_points / decay
        if is_sensor_focused:
            rank *= 1.35
        return rank

    def _is_iot_story(self, title: str) -> bool:
        """Determines if a story is IoT/sensor-related using exact word boundaries."""
        return bool(self.IOT_REGEX.search(title))

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
        Fetches trending stories strictly focused on IoT, sensors, telemetry,
        and embedded hardware news from Hacker News.
        """
        now = int(time.time())
        past_180d = now - (180 * 86400)
        seen_ids = set()
        candidate_stories: List[Story] = []

        search_queries = [
            "IoT",
            "sensor",
            "sensors",
            "ESP32",
            "MQTT",
            "telemetry",
            "embedded hardware",
            "industrial IoT",
            "smart home",
        ]

        async with httpx.AsyncClient(timeout=10.0) as client:
            # 1. Fetch targeted IoT & sensor stories concurrently from Algolia HN API
            algolia_tasks = [
                client.get(
                    "https://hn.algolia.com/api/v1/search",
                    params={
                        "query": q,
                        "tags": "story",
                        "restrictSearchableAttributes": "title",
                        "numericFilters": f"created_at_i>{past_180d}",
                        "hitsPerPage": 20,
                    },
                )
                for q in search_queries
            ]

            # Also fetch latest real-time submissions for IoT and sensor
            algolia_tasks.append(
                client.get("https://hn.algolia.com/api/v1/search_by_date", params={"query": "IoT", "tags": "story", "hitsPerPage": 20})
            )
            algolia_tasks.append(
                client.get("https://hn.algolia.com/api/v1/search_by_date", params={"query": "sensor", "tags": "story", "hitsPerPage": 20})
            )

            # 2. Also check top official Firebase HN stories for any live front-page IoT stories
            firebase_task = client.get(f"{settings.HN_API_BASE}/topstories.json")

            all_tasks = algolia_tasks + [firebase_task]
            results = await asyncio.gather(*all_tasks, return_exceptions=True)

            # Process Algolia results
            algolia_results = results[:-1]
            firebase_res = results[-1]

            for r in algolia_results:
                if not isinstance(r, httpx.Response) or r.status_code != 200:
                    continue
                hits = r.json().get("hits", [])
                for hit in hits:
                    sid = str(hit.get("objectID", ""))
                    title = (hit.get("title") or "").strip()
                    if not sid or sid in seen_ids or not title:
                        continue

                    # Strict IoT & sensor validation
                    if not self._is_iot_story(title):
                        continue

                    seen_ids.add(sid)
                    url = hit.get("url") or f"https://news.ycombinator.com/item?id={sid}"
                    score = hit.get("points") or 0
                    comments_count = hit.get("num_comments") or 0
                    hn_url = f"https://news.ycombinator.com/item?id={sid}"
                    timestamp = hit.get("created_at_i") or int(time.time())
                    published_at = datetime.fromtimestamp(timestamp, tz=timezone.utc)
                    author = hit.get("author", "anonymous")

                    is_sensor_boost = bool(self.SENSOR_MONITORING_BOOST_REGEX.search(title))
                    rank_score = self.calculate_rank_score(score, comments_count, timestamp, is_sensor_focused=is_sensor_boost)

                    candidate_stories.append(
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
                            source_name="Hacker News (IoT & Sensors)",
                        )
                    )

            # Process Firebase HN top stories
            if isinstance(firebase_res, httpx.Response) and firebase_res.status_code == 200:
                try:
                    candidate_ids = [str(sid) for sid in firebase_res.json()[:40] if str(sid) not in seen_ids]
                    items_data = await asyncio.gather(*[self._fetch_item(client, sid) for sid in candidate_ids])

                    for sid, data in zip(candidate_ids, items_data):
                        if not data or data.get("type") != "story" or data.get("deleted") or data.get("dead"):
                            continue

                        title = (data.get("title") or "").strip()
                        if not title or not self._is_iot_story(title):
                            continue

                        url = data.get("url", f"https://news.ycombinator.com/item?id={sid}")
                        score = data.get("score", 0)
                        comments_count = data.get("descendants", 0)
                        hn_url = f"https://news.ycombinator.com/item?id={sid}"
                        timestamp = data.get("time", int(time.time()))
                        published_at = datetime.fromtimestamp(timestamp, tz=timezone.utc)
                        author = data.get("by", "anonymous")

                        is_sensor_boost = bool(self.SENSOR_MONITORING_BOOST_REGEX.search(title))
                        rank_score = self.calculate_rank_score(score, comments_count, timestamp, is_sensor_focused=is_sensor_boost)

                        seen_ids.add(sid)
                        candidate_stories.append(
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
                                source_name="Hacker News (IoT & Sensors)",
                            )
                        )
                except Exception:
                    pass

        # Sort all validated IoT stories by rank score descending
        candidate_stories.sort(key=lambda s: s.rank_score, reverse=True)

        return candidate_stories[:limit]
