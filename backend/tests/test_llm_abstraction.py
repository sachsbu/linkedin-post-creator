import pytest
from app.ai.factory import AIFactory
from app.ai.gemini_provider import GeminiProvider
from app.ai.openai_provider import OpenAIProvider
from app.ai.ollama_provider import OllamaProvider
from app.ai.lmstudio_provider import LMStudioProvider

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

    lmstudio = AIFactory.get_provider("lmstudio")
    assert isinstance(lmstudio, LMStudioProvider)
    assert lmstudio.provider_name == "LMStudio"

    fallback = AIFactory.get_provider("unknown_provider")
    assert fallback.provider_name.lower() == "openai"


def test_dynamic_tone_prompts():
    from app.prompts.linkedin_prompt import get_linkedin_system_prompt, get_linkedin_user_prompt
    from app.models.domain import ArticleSummary

    summary = ArticleSummary(
        what_happened="New Python 3.13 release",
        why_it_matters="JIT compiler included",
        impact="Faster execution",
        key_takeaway="Benchmark your workloads"
    )

    for tone in ["developer", "founder", "investor", "professional"]:
        sys_prompt = get_linkedin_system_prompt(tone)
        usr_prompt = get_linkedin_user_prompt(
            title="Python 3.13 JIT",
            tone=tone,
            source_url="https://python.org",
            what_happened=summary.what_happened,
            why_it_matters=summary.why_it_matters,
            impact=summary.impact,
            key_takeaway=summary.key_takeaway
        )
        assert tone in sys_prompt
        assert tone in usr_prompt


def test_strip_trailing_hashtags():
    from app.ai.base import BaseLLMProvider

    caption_with_trailing = (
        "Scaling IoT infrastructure shouldn't mean scaling your maintenance headaches.\n\n"
        "Real-time visibility is key with #IoTmonitoring for proactive oversight.\n\n"
        "How is your team managing device health at scale?\n\n"
        "#IoTmonitoring #CloudInfrastructure #IoTManagement #PredictiveMaintenance #SmartTech #JediSense"
    )

    cleaned = BaseLLMProvider.strip_trailing_hashtags(caption_with_trailing)
    assert "#IoTmonitoring #CloudInfrastructure" not in cleaned
    assert "#IoTmonitoring for proactive oversight" in cleaned
    assert "How is your team managing device health at scale?" in cleaned



