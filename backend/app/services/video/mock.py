import asyncio
from typing import Tuple, Optional, Dict, Any
from datetime import datetime, timezone
from app.services.video.base import VideoProvider
from app.models.generation import Generation
from app.schemas.common import GenerationStatus
from app.core.exceptions import ProviderFailureException, GenerationTimeoutException


class MockVideoProvider(VideoProvider):
    _jobs: Dict[str, Dict[str, Any]] = {}

    def __init__(self):
        pass

    async def submit_generation(self, generation: Generation) -> str:
        job_id = f"job-{generation.id}"
        
        prompt_lower = generation.original_prompt.lower()
        should_fail = "fail_trigger" in prompt_lower or "force_fail" in prompt_lower
        should_timeout = "timeout_trigger" in prompt_lower or "force_timeout" in prompt_lower

        initial_status = GenerationStatus.QUEUED
        error_msg = None

        if should_fail:
            initial_status = GenerationStatus.FAILED
            error_msg = "Simulated AI Video Provider GPU out-of-memory exception"
        elif should_timeout:
            initial_status = GenerationStatus.TIMED_OUT
            error_msg = "Simulated video generation execution timeout"

        MockVideoProvider._jobs[job_id] = {
            "generation_id": generation.id,
            "created_at": datetime.now(timezone.utc),
            "status": initial_status,
            "progress": 0 if not (should_fail or should_timeout) else None,
            "should_fail": should_fail,
            "should_timeout": should_timeout,
            "error_message": error_msg,
            "model_id": generation.model_id,
            "style": generation.style,
            "aspect_ratio": generation.aspect_ratio,
        }

        if not (should_fail or should_timeout):
            asyncio.create_task(self._simulate_job_lifecycle(job_id))

        return job_id

    async def _simulate_job_lifecycle(self, job_id: str):
        job = MockVideoProvider._jobs.get(job_id)
        if not job or job["should_fail"] or job["should_timeout"]:
            return

        # QUEUED -> SUBMITTED -> GENERATING -> PROCESSING -> COMPLETED
        await asyncio.sleep(0.1)
        job["status"] = GenerationStatus.SUBMITTED
        job["progress"] = 20

        await asyncio.sleep(0.2)
        job["status"] = GenerationStatus.GENERATING
        job["progress"] = 60

        await asyncio.sleep(0.2)
        job["status"] = GenerationStatus.PROCESSING
        job["progress"] = 90

        await asyncio.sleep(0.1)
        job["status"] = GenerationStatus.COMPLETED
        job["progress"] = 100

    async def check_status(self, provider_job_id: str) -> Tuple[GenerationStatus, Optional[int]]:
        job = MockVideoProvider._jobs.get(provider_job_id)
        if not job:
            return GenerationStatus.COMPLETED, 100
        return job["status"], job.get("progress")

    async def get_result(self, provider_job_id: str) -> Dict[str, Any]:
        job = MockVideoProvider._jobs.get(provider_job_id)
        if job and job["status"] == GenerationStatus.FAILED:
            raise ProviderFailureException("MockVideoProvider", job.get("error_message", "Mock render error"))
        if job and job["status"] == GenerationStatus.TIMED_OUT:
            raise GenerationTimeoutException(job.get("generation_id", provider_job_id))

        return {
            "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
            "thumbnail_url": "https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?auto=format&fit=crop&w=1200&q=80",
            "generation_time_seconds": 4.8
        }
