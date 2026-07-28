import json
import logging
from typing import Dict, Any
import httpx
from app.config import settings
from app.models.domain import ArticleSummary
from app.ai.base import BaseLLMProvider
from app.prompts.summary_prompt import SUMMARY_SYSTEM_PROMPT, SUMMARY_USER_PROMPT
from app.prompts.linkedin_prompt import get_linkedin_system_prompt, get_linkedin_user_prompt
from app.ai.gemini_provider import GeminiProvider

logger = logging.getLogger(__name__)

class OllamaProvider(BaseLLMProvider):
    def __init__(self, base_url: str = None, model: str = None):
        self.base_url = base_url or settings.OLLAMA_BASE_URL
        self.model = model or settings.OLLAMA_MODEL or "llama3"


    @property
    def provider_name(self) -> str:
        return "Ollama"

    async def _call_ollama_api(self, system_prompt: str, user_prompt: str) -> str:
        url = f"{self.base_url.rstrip('/')}/api/generate"
        payload = {
            "model": self.model,
            "system": system_prompt,
            "prompt": user_prompt,
            "format": "json",
            "stream": False,
            "options": {"temperature": settings.TEMPERATURE}
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload)
            if response.status_code != 200:
                raise RuntimeError(f"Ollama API error ({response.status_code}): {response.text}")
            data = response.json()
            return data.get("response", "")

    async def summarize_article(self, title: str, content: str, source_url: str) -> ArticleSummary:
        user_prompt = SUMMARY_USER_PROMPT.format(
            title=title,
            source_url=source_url,
            content=content[:2000] if content else "Summarize based on title."
        )

        try:
            raw_text = await self._call_ollama_api(SUMMARY_SYSTEM_PROMPT, user_prompt)
            data = json.loads(raw_text)
            return ArticleSummary(
                what_happened=data.get("what_happened", title),
                why_it_matters=data.get("why_it_matters", "Significant tech development."),
                impact=data.get("impact", "Impacts developer ecosystem."),
                key_takeaway=data.get("key_takeaway", "Stay informed on technical progress.")
            )
        except Exception as e:
            logger.error(f"Ollama summary error: {e}")
            return ArticleSummary(
                what_happened=f"Trending story: {title}",
                why_it_matters="High interest technology topic.",
                impact="Relevant for developers and engineers.",
                key_takeaway="Analyze story details."
            )

    async def generate_linkedin_post(
        self,
        title: str,
        summary: ArticleSummary,
        source_url: str,
        tone: str
    ) -> Dict[str, Any]:
        system_prompt = get_linkedin_system_prompt(tone)
        user_prompt = get_linkedin_user_prompt(
            title=title,
            tone=tone,
            source_url=source_url,
            what_happened=summary.what_happened,
            why_it_matters=summary.why_it_matters,
            impact=summary.impact,
            key_takeaway=summary.key_takeaway
        )

        try:
            raw_text = await self._call_ollama_api(system_prompt, user_prompt)
            data = json.loads(raw_text)
            caption = data.get("caption", "").strip()
            raw_hashtags = data.get("hashtags", [])
            hashtags = GeminiProvider.sanitize_hashtags(raw_hashtags, title)
            return {
                "caption": caption,
                "hashtags": hashtags,
                "word_count": len(caption.split())
            }
        except Exception as e:
            logger.error(f"Ollama post generation error: {e}")
            fallback_caption = f"Tech Update: {title}\n\n{summary.what_happened}"
            tags = GeminiProvider.sanitize_hashtags([], title)
            return {
                "caption": fallback_caption,
                "hashtags": tags,
                "word_count": len(fallback_caption.split())
            }
