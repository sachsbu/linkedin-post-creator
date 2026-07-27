import json
import logging
from typing import Dict, Any
import httpx
from app.config import settings
from app.models.domain import ArticleSummary
from app.ai.base import BaseLLMProvider
from app.prompts.summary_prompt import SUMMARY_SYSTEM_PROMPT, SUMMARY_USER_PROMPT
from app.prompts.linkedin_prompt import LINKEDIN_SYSTEM_PROMPT, LINKEDIN_USER_PROMPT

logger = logging.getLogger(__name__)

class GeminiProvider(BaseLLMProvider):
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.DEFAULT_MODEL or "gemini-2.5-flash"

    @property
    def provider_name(self) -> str:
        return "Gemini"

    async def _call_gemini_api(self, system_prompt: str, user_prompt: str) -> str:
        """Call Gemini REST API directly using httpx for reliable async handling."""
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not configured.")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": f"{system_prompt}\n\n{user_prompt}"}]
                }
            ],
            "generationConfig": {
                "temperature": settings.TEMPERATURE,
                "responseMimeType": "application/json"
            }
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            if response.status_code != 200:
                logger.error(f"Gemini API error ({response.status_code}): {response.text}")
                raise RuntimeError(f"Gemini API request failed: {response.text}")

            data = response.json()
            candidates = data.get("candidates", [])
            if not candidates:
                raise RuntimeError("Gemini returned empty candidates response.")

            text = candidates[0]["content"]["parts"][0]["text"]
            return text

    async def summarize_article(self, title: str, content: str, source_url: str) -> ArticleSummary:
        user_prompt = SUMMARY_USER_PROMPT.format(
            title=title,
            source_url=source_url,
            content=content[:3000] if content else "Content unavailable. Summarize based on story title."
        )

        try:
            raw_text = await self._call_gemini_api(SUMMARY_SYSTEM_PROMPT, user_prompt)
            data = json.loads(raw_text)
            return ArticleSummary(
                what_happened=data.get("what_happened", title),
                why_it_matters=data.get("why_it_matters", "Significant tech movement."),
                impact=data.get("impact", "Impacts software engineering workflows."),
                key_takeaway=data.get("key_takeaway", "Stay updated on recent technical developments.")
            )
        except Exception as e:
            logger.error(f"Fallback summary used due to error: {e}")
            return ArticleSummary(
                what_happened=f"Hacker News top story: {title}",
                why_it_matters="High engagement story on tech front-page.",
                impact="Relevant to developers, engineers, and tech founders.",
                key_takeaway="Evaluate the technology and discussion points."
            )

    async def generate_linkedin_post(
        self,
        title: str,
        summary: ArticleSummary,
        source_url: str,
        tone: str = "professional"
    ) -> Dict[str, Any]:
        user_prompt = LINKEDIN_USER_PROMPT.format(
            title=title,
            tone=tone,
            source_url=source_url,
            what_happened=summary.what_happened,
            why_it_matters=summary.why_it_matters,
            impact=summary.impact,
            key_takeaway=summary.key_takeaway
        )

        try:
            raw_text = await self._call_gemini_api(LINKEDIN_SYSTEM_PROMPT, user_prompt)
            data = json.loads(raw_text)
            caption = data.get("caption", "").strip()
            hashtags = data.get("hashtags", ["#Tech", "#Programming", "#SoftwareEngineering", "#AI", "#Startups"])
            words = len(caption.split())

            return {
                "caption": caption,
                "hashtags": hashtags,
                "word_count": words
            }
        except Exception as e:
            logger.error(f"Fallback post generation used due to error: {e}")
            fallback_caption = (
                f"Big update in tech today: {title}.\n\n"
                f"{summary.what_happened}\n\n"
                f"Why this matters: {summary.why_it_matters}\n\n"
                f"Key takeaway: {summary.key_takeaway}\n\n"
                f"What are your thoughts on this development?"
            )
            tags = ["#TechNews", "#SoftwareEngineering", "#Programming", "#Innovation", "#Tech"]
            return {
                "caption": fallback_caption,
                "hashtags": tags,
                "word_count": len(fallback_caption.split())
            }
