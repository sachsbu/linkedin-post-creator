from abc import ABC, abstractmethod
from typing import List
from app.models.domain import Story

class BaseSourceFetcher(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the news source."""
        pass

    @abstractmethod
    async def fetch_trending_stories(self, limit: int = 20) -> List[Story]:
        """Fetch and rank trending stories from the source."""
        pass
