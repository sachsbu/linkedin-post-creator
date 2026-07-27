import logging
from app.config import settings
from app.ai.base import BaseLLMProvider
from app.ai.gemini_provider import GeminiProvider
from app.ai.openai_provider import OpenAIProvider
from app.ai.ollama_provider import OllamaProvider

logger = logging.getLogger(__name__)

class AIFactory:
    @staticmethod
    def get_provider(provider_name: str = None, model: str = None) -> BaseLLMProvider:
        name = (provider_name or settings.LLM_PROVIDER).lower()

        if name == "gemini":
            return GeminiProvider(model=model)
        elif name == "openai":
            return OpenAIProvider(model=model)
        elif name == "ollama":
            return OllamaProvider(model=model)
        else:
            logger.warning(f"Unknown provider '{name}', defaulting to Gemini")
            return GeminiProvider(model=model)
