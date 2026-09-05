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
    # Positive matches
    assert fetcher._is_iot_story("Building an ESP32 weather station with MQTT") is True
    assert fetcher._is_iot_story("Raspberry Pi Pico W for home automation") is True
    assert fetcher._is_iot_story("Show HN: I replaced a $120k bowling center system with $1,600 in ESP32s") is True
    assert fetcher._is_iot_story("U.S. pulling ocean sensors a shock for Canadian research") is True
    assert fetcher._is_iot_story("Industrial telemetry with MQTT and SCADA") is True
    assert fetcher._is_iot_story("Cloud sensor monitoring platform architecture") is True

    # Negative matches (ensuring word boundaries prevent false positives)
    assert fetcher._is_iot_story("Why Postgres is all you need") is False
    assert fetcher._is_iot_story("I raised 5 kids. Looking back, their careers as adults make perfect sense") is False
    assert fetcher._is_iot_story("Ask HN: Does anyone else feel like nothing matters anymore?") is False
    assert fetcher._is_iot_story("Biggest dark matter detector spots a single weird particle") is False
    assert fetcher._is_iot_story("Desktop AI for ops is still subsidized") is False


@pytest.mark.asyncio
async def test_hacker_news_fetch_trending_stories_iot_ratio():
    fetcher = HackerNewsFetcher()
    stories = await fetcher.fetch_trending_stories(limit=15)
    
    assert len(stories) > 0
    # Verify that 100% of returned stories pass the strict IoT / Sensor validator
    for s in stories:
        assert fetcher._is_iot_story(s.title), f"Non-IoT story found: {s.title}"
        assert s.source_name == "Hacker News (IoT & Sensors)"
