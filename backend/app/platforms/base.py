from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class SocialPlatformGenerator(ABC):
    @property
    @abstractmethod
    def platform_name(self) -> str:
        """Unique key name for the platform (e.g. 'linkedin', 'instagram', 'twitter')"""
        pass

    @abstractmethod
    async def validate_input(self, **kwargs) -> Dict[str, Any]:
        """Validates platform specific inputs before generation."""
        pass

    @abstractmethod
    async def generate_post(self, **kwargs) -> Dict[str, Any]:
        """
        Executes platform-specific content generation.
        Returns dictionary containing generated caption, hashtags, and metadata.
        """
        pass
