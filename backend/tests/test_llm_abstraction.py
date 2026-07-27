import pytest
from app.ai.factory import AIFactory
from app.ai.gemini_provider import GeminiProvider
from app.ai.openai_provider import OpenAIProvider
from app.ai.ollama_provider import OllamaProvider

def test_ai_factory_providers():
    gemini = AIFactory.get_provider("gemini")
    assert isinstance(gemini, GeminiProvider)
    assert gemini.provider_name == "Gemini"

    openai = AIFactory.get_provider("openai")
    assert isinstance(openai, OpenAIProvider)
    assert openai.provider_name == "OpenAI"

    ollama = AIFactory.get_provider("ollama")
    assert isinstance(ollama, OllamaProvider)
    assert ollama.provider_name == "Ollama"

    fallback = AIFactory.get_provider("unknown_provider")
    assert fallback.provider_name.lower() == "openai"

