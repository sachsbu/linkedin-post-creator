import json
import logging
from typing import Dict, Any
import httpx
from app.config import settings
from app.models.domain import ArticleSummary
from app.ai.base import BaseLLMProvider
from app.ai.gemini_provider import GeminiProvider

from app.prompts.summary_prompt import SUMMARY_SYSTEM_PROMPT, SUMMARY_USER_PROMPT
from app.prompts.linkedin_prompt import get_linkedin_system_prompt, get_linkedin_user_prompt

logger = logging.getLogger(__name__)

class OpenAIProvider(BaseLLMProvider):
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.OPENAI_MODEL or "gpt-4o-mini"


    @property
    def provider_name(self) -> str:
        return "OpenAI"

    async def _call_openai_api(self, system_prompt: str, user_prompt: str) -> str:
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not configured.")

        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "response_format": {"type": "json_object"},
            "temperature": settings.TEMPERATURE
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            if response.status_code != 200:
                raise RuntimeError(f"OpenAI API error ({response.status_code}): {response.text}")
            
            data = response.json()
            return data["choices"][0]["message"]["content"]

    async def summarize_article(self, title: str, content: str, source_url: str) -> ArticleSummary:
        user_prompt = SUMMARY_USER_PROMPT.format(
            title=title,
            source_url=source_url,
            content=content[:3000] if content else "Content unavailable. Summarize based on story title."
        )

        try:
            raw_text = await self._call_openai_api(SUMMARY_SYSTEM_PROMPT, user_prompt)
            data = json.loads(raw_text)
            return ArticleSummary(
                what_happened=data.get("what_happened", title),
                why_it_matters=data.get("why_it_matters", "Significant tech movement."),
                impact=data.get("impact", "Impacts software engineering workflows."),
                key_takeaway=data.get("key_takeaway", "Stay updated on recent technical developments.")
            )
        except Exception as e:
            logger.error(f"OpenAI summary error: {e}")
            return ArticleSummary(
                what_happened=f"Hacker News story: {title}",
                why_it_matters="High engagement story on tech front-page.",
                impact="Relevant to developers and founders.",
                key_takeaway="Evaluate technical implications."
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
            raw_text = await self._call_openai_api(system_prompt, user_prompt)
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
            logger.error(f"OpenAI post generation error: {e}")
            fallback_caption = f"Tech Update: {title}\n\n{summary.what_happened}\n\nKey Takeaway: {summary.key_takeaway}"
            tags = GeminiProvider.sanitize_hashtags([], title)
            return {
                "caption": fallback_caption,
                "hashtags": tags,
                "word_count": len(fallback_caption.split())
            }

