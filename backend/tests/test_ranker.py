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
