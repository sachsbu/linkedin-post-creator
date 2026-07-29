import pytest
from app.ai.gemini_provider import GeminiProvider
from app.prompts.instagram_prompt import get_instagram_system_prompt, get_instagram_user_prompt

def test_instagram_prompt_building():
    sys_prompt = get_instagram_system_prompt()
    user_prompt = get_instagram_user_prompt("Launching our new AI automation tool", media_type="image")

    assert "Maximum 2 concise, impactful sentences" in sys_prompt
    assert "8 to 10 highly relevant hashtags" in sys_prompt
    assert "Launching our new AI automation tool" in user_prompt


def test_sanitize_instagram_hashtags():
    raw_tags = ["#AI", "#Tech", "#Automation", "#MachineLearning", "#Python", "#SaaS"]
    prompt = "Launching an automated platform for developers and startups"
    
    tags = GeminiProvider.sanitize_instagram_hashtags(raw_tags, prompt)
    
    # Needs 8 to 10 hashtags
    assert len(tags) >= 8 and len(tags) <= 10
    # No duplicates
    assert len(tags) == len(set([t.lower() for t in tags]))
    # All start with #
    assert all(t.startswith("#") for t in tags)
