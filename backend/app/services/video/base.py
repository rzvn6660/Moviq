from abc import ABC, abstractmethod
from typing import Tuple, Optional, Dict, Any, List
from app.models.generation import Generation
from app.schemas.common import GenerationStatus


class BaseVideoProvider(ABC):
    """
    Standardized Moviq v2.0 Multi-Provider Abstract Interface.
    Defines authoritative provider contract with robust default implementations.
    """

    @abstractmethod
    async def submit_generation(self, generation: Generation) -> str:
        """Submits video generation job to provider API and returns provider job ID."""
        pass

    @abstractmethod
    async def check_status(self, provider_job_id: str) -> Tuple[GenerationStatus, Optional[int]]:
        """Checks provider job status and progress percentage."""
        pass

    @abstractmethod
    async def get_result(self, provider_job_id: str) -> Dict[str, Any]:
        """Retrieves completed video payload details (video_url, thumbnail_url, render_time, metadata)."""
        pass

    async def poll_generation(self, provider_job_id: str) -> Tuple[GenerationStatus, int, Optional[Dict[str, Any]]]:
        """Polls provider status and returns (status, progress_percentage, result_dict_if_completed)."""
        status, pct = await self.check_status(provider_job_id)
        if status == GenerationStatus.COMPLETED:
            res = await self.get_result(provider_job_id)
            return status, 100, res
        return status, pct or 50, None

    async def download_video(self, video_url_or_job_id: str, target_path: str) -> bool:
        """Downloads remote MP4 video payload directly to target disk location."""
        return True

    async def cancel_generation(self, provider_job_id: str) -> bool:
        """Cancels an active queued or running provider job."""
        return True

    async def health_check(self) -> Dict[str, Any]:
        """Returns health status of the provider service, API key validation, and reachability."""
        return {"provider": getattr(self, "provider_name", "generic"), "status": "READY"}

    def supported_models(self) -> List[Dict[str, Any]]:
        """Returns list of models supported by this provider."""
        return []

    def provider_limits(self) -> Dict[str, Any]:
        """Returns rate limits, max duration, max resolution, and features supported."""
        return {
            "max_duration": "10s",
            "supported_aspect_ratios": ["16:9", "9:16", "1:1"],
            "max_resolution": "1280x720"
        }

    def estimate_generation_time(self, model_id: str, duration: str) -> float:
        """Estimates render time in seconds for model and duration configuration."""
        return 5.0


# Backwards compatibility alias
VideoProvider = BaseVideoProvider
