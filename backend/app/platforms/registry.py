from typing import Dict, Type
from app.platforms.base import SocialPlatformGenerator
from app.platforms.linkedin import LinkedInGenerator
from app.platforms.instagram import InstagramGenerator

class PlatformRegistry:
    """
    Registry for managing social platform generators using the Strategy Pattern.
    Allows easy addition of future platforms (Twitter, Facebook, Threads, Medium, Dev.to).
    """
    _generators: Dict[str, SocialPlatformGenerator] = {}

    @classmethod
    def register_generator(cls, platform_name: str, generator: SocialPlatformGenerator) -> None:
        cls._generators[platform_name.lower().strip()] = generator

    @classmethod
    def get_generator(cls, platform_name: str) -> SocialPlatformGenerator:
        key = platform_name.lower().strip()
        if key not in cls._generators:
            raise KeyError(
                f"Platform '{platform_name}' is not registered. Available platforms: {list(cls._generators.keys())}"
            )
        return cls._generators[key]

    @classmethod
    def list_supported_platforms(cls) -> list:
        return list(cls._generators.keys())


# Default registration
platform_registry = PlatformRegistry()
platform_registry.register_generator("linkedin", LinkedInGenerator())
platform_registry.register_generator("instagram", InstagramGenerator())
