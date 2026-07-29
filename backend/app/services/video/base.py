from abc import ABC, abstractmethod
from typing import Tuple, Optional, Dict, Any
from app.models.generation import Generation
from app.schemas.common import GenerationStatus


class VideoProvider(ABC):
    @abstractmethod
    async def submit_generation(self, generation: Generation) -> str:
        """Submits video generation job to provider engine."""
        pass

    @abstractmethod
    async def check_status(self, provider_job_id: str) -> Tuple[GenerationStatus, Optional[int]]:
        """Checks provider job status and percentage if available."""
        pass

    @abstractmethod
    async def get_result(self, provider_job_id: str) -> Dict[str, Any]:
        """Gets generated video assets (video_url, thumbnail_url, render_time)."""
        pass
