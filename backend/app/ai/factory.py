import logging
from app.config import settings
from app.ai.base import BaseLLMProvider
from app.ai.gemini_provider import GeminiProvider
from app.ai.openai_provider import OpenAIProvider
from app.ai.ollama_provider import OllamaProvider
from app.ai.lmstudio_provider import LMStudioProvider

logger = logging.getLogger(__name__)

class AIFactory:
    @staticmethod
    def get_provider(provider_name: str = None, model: str = None) -> BaseLLMProvider:
        # If provider_name is not explicitly passed, read LLM_PROVIDER from .env settings
        if not provider_name or not provider_name.strip():
            provider_name = settings.LLM_PROVIDER

        name = provider_name.lower().strip()

        if name == "openai":
            selected_model = model or settings.OPENAI_MODEL
            logger.info(f"Instantiating OpenAI Provider (model: {selected_model})")
            return OpenAIProvider(model=selected_model)
        elif name == "ollama":
            selected_model = model or settings.OLLAMA_MODEL
            logger.info(f"Instantiating Ollama Provider (model: {selected_model})")
            return OllamaProvider(model=selected_model)
        elif name in ["lmstudio", "lm_studio", "lm-studio"]:
            selected_model = model or settings.LMSTUDIO_MODEL
            logger.info(f"Instantiating LMStudio Provider (model: {selected_model})")
            return LMStudioProvider(model=selected_model)
        elif name == "gemini":
            selected_model = model or settings.GEMINI_MODEL
            logger.info(f"Instantiating Gemini Provider (model: {selected_model})")
            return GeminiProvider(model=selected_model)
        else:
            env_provider = (settings.LLM_PROVIDER or "gemini").lower().strip()
            logger.warning(f"Unknown provider '{name}', falling back to .env LLM_PROVIDER '{env_provider}'")
            if env_provider == "openai":
                return OpenAIProvider(model=model or settings.OPENAI_MODEL)
            elif env_provider == "ollama":
                return OllamaProvider(model=model or settings.OLLAMA_MODEL)
            elif env_provider in ["lmstudio", "lm_studio", "lm-studio"]:
                return LMStudioProvider(model=model or settings.LMSTUDIO_MODEL)
            else:
                return GeminiProvider(model=model or settings.GEMINI_MODEL)
