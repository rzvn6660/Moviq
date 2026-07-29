import httpx
from typing import Tuple, Optional, Dict, Any
from app.services.video.base import VideoProvider
from app.models.generation import Generation
from app.schemas.common import GenerationStatus
from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import (
    FalConfigurationErrorException,
    FalAuthenticationErrorException,
    FalRateLimitedException,
    FalProviderUnavailableException,
    FalSubmissionFailedException,
    FalStatusErrorException,
    FalResultErrorException,
    ProviderFailureException,
)


class FalVideoProvider(VideoProvider):
    """
    fal-ai Async Queue Video Provider implementation.
    Target Model: fal-ai/kling-video/v2.5-turbo/pro/text-to-video
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout_seconds: float = 15.0,
    ):
        self.api_key = api_key if api_key is not None else settings.FAL_KEY
        self.model = model or settings.FAL_MODEL
        self.timeout_seconds = timeout_seconds

    def _get_headers(self) -> Dict[str, str]:
        if not self.api_key or not self.api_key.strip():
            raise FalConfigurationErrorException("FAL_KEY is not configured on the backend server")
        return {
            "Authorization": f"Key {self.api_key.strip()}",
            "Content-Type": "application/json",
        }

    async def submit_generation(self, generation: Generation) -> str:
        headers = self._get_headers()
        url = f"https://queue.fal.run/{self.model}"

        # Clean duration parameter (e.g. "5s" -> "5")
        duration_clean = generation.duration.replace("s", "") if generation.duration else "5"

        prompt_to_use = generation.enhanced_prompt or generation.original_prompt

        payload = {
            "prompt": prompt_to_use,
            "duration": duration_clean,
            "aspect_ratio": generation.aspect_ratio or "16:9",
            "cfg_scale": 0.5,
        }

        if generation.negative_prompt:
            payload["negative_prompt"] = generation.negative_prompt

        logger.info(f"Submitting generation '{generation.id}' to fal queue ({self.model})")

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(url, headers=headers, json=payload)

            if response.status_code in (401, 403):
                logger.error("fal API authentication failed (401/403)")
                raise FalAuthenticationErrorException()
            elif response.status_code == 429:
                logger.warn("fal API rate limited (429)")
                raise FalRateLimitedException()
            elif response.status_code >= 500:
                logger.error(f"fal API provider error ({response.status_code})")
                raise FalProviderUnavailableException(f"fal HTTP {response.status_code}")
            elif response.status_code not in (200, 201, 202):
                logger.error(f"fal submission error ({response.status_code}): {response.text[:200]}")
                raise FalSubmissionFailedException(f"fal HTTP {response.status_code}")

            res_json = response.json()
            request_id = res_json.get("request_id")
            if not request_id:
                raise FalSubmissionFailedException("fal-ai queue response missing request_id")

            logger.info(f"fal-ai generation queued successfully with request_id '{request_id}'")
            return request_id

        except httpx.RequestError as err:
            logger.error(f"Network error submitting to fal-ai: {err}")
            raise FalProviderUnavailableException(f"Network error submitting to fal-ai: {str(err)}")

    async def check_status(self, provider_job_id: str) -> Tuple[GenerationStatus, Optional[int]]:
        headers = self._get_headers()
        url = f"https://queue.fal.run/{self.model}/requests/{provider_job_id}/status"

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.get(url, headers=headers)

            if response.status_code in (401, 403):
                raise FalAuthenticationErrorException()
            elif response.status_code == 429:
                raise FalRateLimitedException()
            elif response.status_code >= 500:
                raise FalProviderUnavailableException()
            elif response.status_code != 200:
                raise FalStatusErrorException(f"fal status HTTP {response.status_code}")

            res_json = response.json()
            status_str = res_json.get("status", "").upper()

            if status_str == "IN_QUEUE":
                return GenerationStatus.SUBMITTED, 20
            elif status_str == "IN_PROGRESS":
                progress = res_json.get("logs", [{}])[-1].get("progress") if res_json.get("logs") else 60
                return GenerationStatus.GENERATING, progress or 60
            elif status_str == "COMPLETED":
                return GenerationStatus.COMPLETED, 100
            elif status_str in ("FAILED", "ERROR"):
                error_msg = res_json.get("error", "fal-ai task reported failure")
                raise ProviderFailureException("fal-ai", str(error_msg))

            return GenerationStatus.GENERATING, 50

        except httpx.RequestError as err:
            logger.warn(f"Network error polling fal status: {err}")
            raise FalStatusErrorException(str(err))

    async def get_result(self, provider_job_id: str) -> Dict[str, Any]:
        headers = self._get_headers()
        url = f"https://queue.fal.run/{self.model}/requests/{provider_job_id}"

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.get(url, headers=headers)

            if response.status_code != 200:
                raise FalResultErrorException(f"fal result query returned HTTP {response.status_code}")

            res_json = response.json()
            
            video_url = None
            if "video" in res_json and isinstance(res_json["video"], dict):
                video_url = res_json["video"].get("url")
            elif "video_url" in res_json:
                video_url = res_json["video_url"]

            if not video_url:
                logger.error(f"fal-ai result JSON missing video URL: {res_json}")
                raise FalResultErrorException("fal-ai response payload missing valid video URL")

            thumbnail_url = None
            if "thumbnail" in res_json and isinstance(res_json["thumbnail"], dict):
                thumbnail_url = res_json["thumbnail"].get("url")
            elif "thumbnail_url" in res_json:
                thumbnail_url = res_json["thumbnail_url"]

            return {
                "video_url": video_url,
                "thumbnail_url": thumbnail_url or "https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?auto=format&fit=crop&w=1200&q=80",
                "generation_time_seconds": res_json.get("timings", {}).get("inference", 4.8)
            }

        except httpx.RequestError as err:
            logger.error(f"Network error fetching fal-ai result: {err}")
            raise FalResultErrorException(str(err))
