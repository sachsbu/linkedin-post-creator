from typing import Dict
from app.sources.base import BaseSourceFetcher
from app.sources.hacker_news import HackerNewsFetcher
from app.sources.cnet import CNETFetcher

class SourceRegistry:
    def __init__(self):
        self._sources: Dict[str, BaseSourceFetcher] = {}
        # Register default sources
        self.register(HackerNewsFetcher())
        self.register(CNETFetcher())


    def register(self, fetcher: BaseSourceFetcher):
        self._sources[fetcher.name.lower().replace(" ", "_")] = fetcher

    def get(self, name: str) -> BaseSourceFetcher:
        key = name.lower().replace(" ", "_")
        if key not in self._sources:
            # Fallback to Hacker News if unknown
            return self._sources.get("hacker_news", HackerNewsFetcher())
        return self._sources[key]

    def list_sources(self) -> Dict[str, str]:
        return {key: fetcher.name for key, fetcher in self._sources.items()}

source_registry = SourceRegistry()
