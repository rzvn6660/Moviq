import os
import uuid
import time
import asyncio
import httpx
from typing import Tuple, Optional, Dict, Any

from app.services.video.base import VideoProvider
from app.models.generation import Generation
from app.schemas.common import GenerationStatus
from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import (
    RemoteWANConfigurationErrorException,
    RemoteWANUnavailableException,
    RemoteWANTimeoutException,
    RemoteWANAuthenticationErrorException,
    RemoteWANGenerationFailedException,
    RemoteWANInvalidResultException,
)


# Module-level job status storage for in-flight Remote Wan2.1 inference tasks
_REMOTE_WAN_JOBS: Dict[str, Dict[str, Any]] = {}


class RemoteWanVideoProvider(VideoProvider):
    """
    Remote Wan2.1 T2V 1.3B Video Provider.
    Delegates video generation to a remote GPU worker service hosting Wan2.1.
    Downloads the resulting MP4 server-side and serves it via local media endpoints.
    """

    def __init__(
        self,
        remote_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
    ):
        raw_url = remote_url if remote_url is not None else settings.REMOTE_WAN_URL
        self.remote_url = (raw_url or "").rstrip("/")
        self.api_key = api_key if api_key is not None else settings.REMOTE_WAN_API_KEY
        self.timeout_seconds = timeout_seconds or settings.REMOTE_WAN_TIMEOUT_SECONDS

    async def submit_generation(self, generation: Generation) -> str:
        if not self.remote_url:
            logger.error("RemoteWanVideoProvider requested but REMOTE_WAN_URL is not configured")
            raise RemoteWANConfigurationErrorException()

        job_id = f"remote-wan-job-{uuid.uuid4().hex[:8]}"
        _REMOTE_WAN_JOBS[job_id] = {
            "status": GenerationStatus.GENERATING,
            "progress": 25,
            "generation_id": generation.id,
            "result": None,
            "error": None,
        }

        prompt_to_use = generation.enhanced_prompt or generation.original_prompt
        negative_prompt = generation.negative_prompt

        logger.info(f"Submitting generation '{generation.id}' to remote Wan2.1 GPU worker '{self.remote_url}' (job_id='{job_id}')")

        asyncio.create_task(
            self._execute_remote_wan_inference(
                generation_id=generation.id,
                job_id=job_id,
                prompt=prompt_to_use,
                negative_prompt=negative_prompt
            )
        )

        return job_id

    async def _execute_remote_wan_inference(
        self,
        generation_id: str,
        job_id: str,
        prompt: str,
        negative_prompt: Optional[str] = None
    ):
        start_time = time.time()

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {
            "generation_id": generation_id,
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "width": 576,
            "height": 320,
            "num_frames": 33,
            "num_inference_steps": settings.WAN_NUM_INFERENCE_STEPS,
            "guidance_scale": settings.WAN_GUIDANCE_SCALE,
            "fps": settings.WAN_FPS
        }

        try:
            async with httpx.AsyncClient(timeout=float(self.timeout_seconds)) as client:
                generate_endpoint = f"{self.remote_url}/generate"
                logger.info(f"Sending remote generation request to {generate_endpoint}...")

                resp = await client.post(generate_endpoint, json=payload, headers=headers)

                if resp.status_code in (401, 403):
                    logger.error(f"Remote Wan worker authentication error ({resp.status_code})")
                    raise RemoteWANAuthenticationErrorException()

                if resp.status_code != 200:
                    err_msg = f"Remote Wan worker returned HTTP {resp.status_code}: {resp.text}"
                    logger.error(err_msg)
                    raise RemoteWANGenerationFailedException(err_msg)

                data = resp.json()
                remote_video_url = data.get("video_url")
                if not remote_video_url:
                    raise RemoteWANInvalidResultException("Remote worker response missing 'video_url'")

                # Resolve absolute URL if relative
                if remote_video_url.startswith("/"):
                    remote_video_url = f"{self.remote_url}{remote_video_url}"

                # Download MP4 binary from remote worker server-side
                logger.info(f"Downloading rendered MP4 from remote worker: {remote_video_url}")
                dl_resp = await client.get(remote_video_url, headers=headers)
                if dl_resp.status_code != 200:
                    raise RemoteWANInvalidResultException(f"Failed to download remote MP4 (HTTP {dl_resp.status_code})")

                video_bytes = dl_resp.content
                if not video_bytes or len(video_bytes) == 0:
                    raise RemoteWANInvalidResultException("Downloaded MP4 from remote worker is empty (0 bytes)")

                # Save locally under backend/generated/moviq_<generation_id>.mp4
                generated_dir = os.path.abspath(os.path.join(os.getcwd(), "generated"))
                os.makedirs(generated_dir, exist_ok=True)
                filepath = os.path.abspath(os.path.join(generated_dir, f"moviq_{generation_id}.mp4"))

                with open(filepath, "wb") as f:
                    f.write(video_bytes)

                if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
                    raise RemoteWANInvalidResultException("Saved local MP4 file is empty or invalid")

                elapsed = round(time.time() - start_time, 2)
                logger.info(f"Remote Wan2.1 generation complete ({len(video_bytes)} bytes in {elapsed}s): {filepath}")

                _REMOTE_WAN_JOBS[job_id]["status"] = GenerationStatus.COMPLETED
                _REMOTE_WAN_JOBS[job_id]["progress"] = 100
                _REMOTE_WAN_JOBS[job_id]["result"] = {
                    "video_url": f"/api/v1/generations/{generation_id}/video",
                    "thumbnail_url": "",
                    "generation_time_seconds": elapsed,
                    "is_synthetic": False
                }

        except (httpx.ConnectError, httpx.ConnectTimeout) as err:
            logger.error(f"Connection to remote Wan worker failed: {err}")
            exc = RemoteWANUnavailableException(f"Remote Wan GPU worker is offline or unreachable: {err}")
            _REMOTE_WAN_JOBS[job_id]["status"] = GenerationStatus.FAILED
            _REMOTE_WAN_JOBS[job_id]["error"] = exc

        except httpx.ReadTimeout as err:
            logger.error(f"Remote Wan worker request timed out: {err}")
            exc = RemoteWANTimeoutException(f"Remote Wan GPU worker request timed out: {err}")
            _REMOTE_WAN_JOBS[job_id]["status"] = GenerationStatus.FAILED
            _REMOTE_WAN_JOBS[job_id]["error"] = exc

        except Exception as err:
            logger.error(f"Remote Wan generation execution error: {err}")
            exc = err if isinstance(err, (RemoteWANConfigurationErrorException, RemoteWANUnavailableException, RemoteWANTimeoutException, RemoteWANAuthenticationErrorException, RemoteWANGenerationFailedException, RemoteWANInvalidResultException)) else RemoteWANGenerationFailedException(str(err))
            _REMOTE_WAN_JOBS[job_id]["status"] = GenerationStatus.FAILED
            _REMOTE_WAN_JOBS[job_id]["error"] = exc

    async def check_status(self, provider_job_id: str) -> Tuple[GenerationStatus, Optional[int]]:
        job = _REMOTE_WAN_JOBS.get(provider_job_id)
        if not job:
            return GenerationStatus.GENERATING, 50

        if job["status"] == GenerationStatus.FAILED and job.get("error"):
            raise job["error"]

        return job["status"], job.get("progress", 50)

    async def get_result(self, provider_job_id: str) -> Dict[str, Any]:
        job = _REMOTE_WAN_JOBS.get(provider_job_id)
        if not job or not job.get("result"):
            raise RemoteWANInvalidResultException("No valid result found for Remote Wan job")
        return job["result"]
