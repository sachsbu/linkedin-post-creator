from abc import ABC, abstractmethod
from typing import Dict, Any, List
from app.models.domain import ArticleSummary

class BaseLLMProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @abstractmethod
    async def summarize_article(self, title: str, content: str, source_url: str) -> ArticleSummary:
        """Generates structured summary of what happened, why it matters, impact, and key takeaway."""
        pass

    @abstractmethod
    async def generate_linkedin_post(
        self,
        title: str,
        summary: ArticleSummary,
        source_url: str,
        tone: str = "professional"
    ) -> Dict[str, Any]:
        """
        Generates engaging LinkedIn post (hook, 2-4 short paragraphs, practical insight, CTA)
        max 180 words, plus 5-8 relevant hashtags.
        Returns dict with keys: 'caption', 'hashtags', 'word_count'.
        """
        pass
