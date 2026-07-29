from abc import ABC, abstractmethod
from app.schemas.director import EnhancePromptResponse


class DirectorProvider(ABC):
    @abstractmethod
    async def enhance_prompt(self, prompt: str) -> EnhancePromptResponse:
        """Enhances raw idea prompt into structured AI Director prompt direction."""
        pass
