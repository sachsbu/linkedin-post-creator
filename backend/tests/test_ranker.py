import pytest
import time
from app.sources.hacker_news import HackerNewsFetcher

def test_hacker_news_rank_decay():
    fetcher = HackerNewsFetcher()
    now = time.time()
    
    # Story 1: 500 score, 100 comments, 1 hour old
    score1 = fetcher.calculate_rank_score(500, 100, now - 3600)
    
    # Story 2: 500 score, 100 comments, 48 hours old
    score2 = fetcher.calculate_rank_score(500, 100, now - (48 * 3600))
    
    # Recent story should rank significantly higher than 48h old story with same points
    assert score1 > score2


def test_hacker_news_is_iot_story():
    fetcher = HackerNewsFetcher()
    assert fetcher._is_iot_story("Building an ESP32 weather station with MQTT") is True
    assert fetcher._is_iot_story("Raspberry Pi Pico W for home automation") is True
    assert fetcher._is_iot_story("Why Postgres is all you need") is False


@pytest.mark.asyncio
async def test_hacker_news_fetch_trending_stories_iot_ratio():
    fetcher = HackerNewsFetcher()
    stories = await fetcher.fetch_trending_stories(limit=15)
    
    assert len(stories) == 15
    iot_count = sum(1 for s in stories if "IoT" in s.source_name or fetcher._is_iot_story(s.title))
    # Verify that at least 10 stories out of 15 are IoT related
    assert iot_count >= 10
