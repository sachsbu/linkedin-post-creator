import pytest
from app.platforms.registry import platform_registry, PlatformRegistry
from app.platforms.linkedin import LinkedInGenerator
from app.platforms.instagram import InstagramGenerator

def test_platform_strategy_registration():
    linkedin_gen = platform_registry.get_generator("linkedin")
    instagram_gen = platform_registry.get_generator("instagram")

    assert isinstance(linkedin_gen, LinkedInGenerator)
    assert isinstance(instagram_gen, InstagramGenerator)
    assert linkedin_gen.platform_name == "linkedin"
    assert instagram_gen.platform_name == "instagram"

    supported = platform_registry.list_supported_platforms()
    assert "linkedin" in supported
    assert "instagram" in supported


def test_invalid_platform_lookup():
    with pytest.raises(KeyError):
        platform_registry.get_generator("unsupported_platform")
