import json
import logging
from typing import Dict, Any
import httpx
from app.config import settings
from app.models.domain import ArticleSummary
from app.ai.base import BaseLLMProvider
from app.prompts.summary_prompt import SUMMARY_SYSTEM_PROMPT, SUMMARY_USER_PROMPT
from app.prompts.linkedin_prompt import get_linkedin_system_prompt, get_linkedin_user_prompt
from app.prompts.instagram_prompt import get_instagram_system_prompt, get_instagram_user_prompt

logger = logging.getLogger(__name__)

class GeminiProvider(BaseLLMProvider):
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_MODEL or "gemini-2.5-flash"


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
            raw_text = await self._call_gemini_api(system_prompt, user_prompt)
            data = json.loads(raw_text)
            caption = self.strip_trailing_hashtags(data.get("caption", "").strip())
            raw_hashtags = data.get("hashtags", [])
            hashtags = self.sanitize_hashtags(raw_hashtags, title)
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
            tags = self.sanitize_hashtags([], title)
            return {
                "caption": fallback_caption,
                "hashtags": tags,
                "word_count": len(fallback_caption.split())
            }

    async def generate_instagram_post(
        self,
        prompt: str,
        media_type: str = "image"
    ) -> Dict[str, Any]:
        system_prompt = get_instagram_system_prompt()
        user_prompt = get_instagram_user_prompt(prompt_idea=prompt, media_type=media_type)

        try:
            raw_text = await self._call_gemini_api(system_prompt, user_prompt)
            data = json.loads(raw_text)
            caption = data.get("caption", "").strip()
            raw_hashtags = data.get("hashtags", [])
            hashtags = self.sanitize_instagram_hashtags(raw_hashtags, prompt)

            return {
                "caption": caption,
                "hashtags": hashtags
            }
        except Exception as e:
            logger.error(f"Gemini Instagram post generation error: {e}")
            fallback_caption = f"{prompt.strip()}.\n\nWhat do you think? Let us know below."
            tags = self.sanitize_instagram_hashtags([], prompt)
            return {
                "caption": fallback_caption,
                "hashtags": tags
            }

    @staticmethod
    def sanitize_instagram_hashtags(raw_hashtags: list, prompt: str) -> list:
        cleaned = []
        if isinstance(raw_hashtags, list):
            for tag in raw_hashtags:
                if isinstance(tag, str):
                    tag_clean = tag.strip().replace(" ", "").replace("#", "")
                    if tag_clean and len(tag_clean) > 1:
                        cleaned.append(f"#{tag_clean}")

        seen = set()
        unique_tags = []
        for tag in cleaned:
            if tag.lower() not in seen:
                seen.add(tag.lower())
                unique_tags.append(tag)

        if len(unique_tags) < 8:
            import re
            words = re.findall(r'[A-Za-z0-9]+', prompt)
            stopwords = {"with", "from", "that", "this", "have", "releases", "shows", "about", "your", "more", "what", "would", "like", "post", "communicate"}
            for w in words:
                if len(w) > 3 and w.lower() not in stopwords:
                    tt = f"#{w.capitalize()}"
                    if tt.lower() not in seen:
                        seen.add(tt.lower())
                        unique_tags.append(tt)
                        if len(unique_tags) >= 10:
                            break

        defaults = [
            "#Tech", "#TechStartup", "#Innovation", "#Programming",
            "#Automation", "#DeveloperLife", "#MachineLearning", "#SaaS",
            "#BuildInPublic", "#TechCommunity", "#SoftwareEngineering"
        ]
        for d in defaults:
            if len(unique_tags) >= 8:
                break
            if d.lower() not in seen:
                seen.add(d.lower())
                unique_tags.append(d)

        return unique_tags[:10]

    @staticmethod
    def sanitize_hashtags(raw_hashtags: list, title: str) -> list:
        cleaned = []
        if isinstance(raw_hashtags, list):
            for tag in raw_hashtags:
                if isinstance(tag, str):
                    tag_clean = tag.strip().replace(" ", "").replace("#", "")
                    if tag_clean and len(tag_clean) > 1:
                        cleaned.append(f"#{tag_clean}")

        seen = set()
        unique_tags = []
        for tag in cleaned:
            if tag.lower() not in seen:
                seen.add(tag.lower())
                unique_tags.append(tag)

        if len(unique_tags) < 5:
            import re
            words = re.findall(r'[A-Za-z0-9]+', title)
            stopwords = {"with", "from", "that", "this", "have", "releases", "shows", "about", "your", "more"}
            for w in words:
                if len(w) > 3 and w.lower() not in stopwords:
                    tt = f"#{w.capitalize()}"
                    if tt.lower() not in seen:
                        seen.add(tt.lower())
                        unique_tags.append(tt)
                        if len(unique_tags) >= 6:
                            break

        defaults = ["#TechNews", "#SoftwareEngineering", "#Innovation", "#Programming", "#Tech"]
        for d in defaults:
            if len(unique_tags) >= 5:
                break
            if d.lower() not in seen:
                seen.add(d.lower())
                unique_tags.append(d)

        return unique_tags[:6]

