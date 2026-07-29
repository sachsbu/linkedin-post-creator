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
from app.ai.gemini_provider import GeminiProvider

logger = logging.getLogger(__name__)


def _clean_json_text(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    return cleaned.strip()


class LMStudioProvider(BaseLLMProvider):
    def __init__(self, url: str = None, model: str = None):
        raw_url = url or settings.LMSTUDIO_URL or "http://localhost:1234/v1/chat/completions"
        if not raw_url.endswith("/chat/completions"):
            clean_base = raw_url.rstrip("/")
            if "/v1" in clean_base:
                self.url = f"{clean_base}/chat/completions"
            else:
                self.url = f"{clean_base}/v1/chat/completions"
        else:
            self.url = raw_url

        self.model = model or settings.LMSTUDIO_MODEL or "google/gemma-4-12b-qat"

    @property
    def provider_name(self) -> str:
        return "LMStudio"

    def _sync_call_lmstudio(self, system_prompt: str, user_prompt: str) -> str:
        headers = {"Content-Type": "application/json"}
        base_payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": settings.TEMPERATURE,
            "stream": False
        }

        with httpx.Client(timeout=300.0) as client:
            # Try 1: with response_format json_object
            try:
                payload_json_fmt = {**base_payload, "response_format": {"type": "json_object"}}
                res = client.post(self.url, json=payload_json_fmt, headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    return data["choices"][0]["message"]["content"]
                logger.warning(f"LMStudio JSON format mode returned status {res.status_code}: {res.text}. Retrying without response_format.")
            except Exception as e:
                logger.warning(f"LMStudio JSON format request exception: {e}")

            # Try 2: without response_format
            try:
                res = client.post(self.url, json=base_payload, headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    return data["choices"][0]["message"]["content"]
                logger.warning(f"LMStudio standard call returned status {res.status_code}: {res.text}. Retrying without model parameter.")
            except Exception as e:
                logger.warning(f"LMStudio standard call exception: {e}")

            # Try 3: without model parameter (LMStudio defaults to loaded model)
            payload_no_model = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": settings.TEMPERATURE,
                "stream": False
            }
            res = client.post(self.url, json=payload_no_model, headers=headers)
            if res.status_code == 200:
                data = res.json()
                return data["choices"][0]["message"]["content"]

            raise RuntimeError(f"LMStudio API error ({res.status_code}): {res.text}")

    async def _call_lmstudio_api(self, system_prompt: str, user_prompt: str) -> str:
        import asyncio
        return await asyncio.to_thread(self._sync_call_lmstudio, system_prompt, user_prompt)

    async def summarize_article(self, title: str, content: str, source_url: str) -> ArticleSummary:
        user_prompt = SUMMARY_USER_PROMPT.format(
            title=title,
            source_url=source_url,
            content=content[:3000] if content else "Content unavailable. Summarize based on story title."
        )

        try:
            raw_text = await self._call_lmstudio_api(SUMMARY_SYSTEM_PROMPT, user_prompt)
            data = json.loads(_clean_json_text(raw_text))
            return ArticleSummary(
                what_happened=data.get("what_happened", title),
                why_it_matters=data.get("why_it_matters", "Significant tech movement."),
                impact=data.get("impact", "Impacts software engineering workflows."),
                key_takeaway=data.get("key_takeaway", "Stay updated on recent technical developments.")
            )
        except Exception as e:
            logger.error(f"LMStudio summary error: {e}")
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
            raw_text = await self._call_lmstudio_api(system_prompt, user_prompt)
            data = json.loads(_clean_json_text(raw_text))
            caption = data.get("caption", "").strip()
            raw_hashtags = data.get("hashtags", [])
            hashtags = GeminiProvider.sanitize_hashtags(raw_hashtags, title)
            return {
                "caption": caption,
                "hashtags": hashtags,
                "word_count": len(caption.split())
            }
        except Exception as e:
            logger.error(f"LMStudio post generation error: {e}")
            fallback_caption = f"Tech Update: {title}\n\n{summary.what_happened}\n\nKey Takeaway: {summary.key_takeaway}"
            tags = GeminiProvider.sanitize_hashtags([], title)
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
            raw_text = await self._call_lmstudio_api(system_prompt, user_prompt)
            data = json.loads(_clean_json_text(raw_text))
            caption = data.get("caption", "").strip()
            raw_hashtags = data.get("hashtags", [])
            hashtags = GeminiProvider.sanitize_instagram_hashtags(raw_hashtags, prompt)
            return {
                "caption": caption,
                "hashtags": hashtags
            }
        except Exception as e:
            logger.error(f"LMStudio Instagram post generation error: {e}")
            fallback_caption = f"{prompt.strip()}.\n\nWhat do you think? Let us know below."
            tags = GeminiProvider.sanitize_instagram_hashtags([], prompt)
            return {
                "caption": fallback_caption,
                "hashtags": tags
            }

