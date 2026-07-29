import os
import uuid
import time
import asyncio
from typing import Tuple, Optional, Dict, Any
from huggingface_hub import InferenceClient
from huggingface_hub.utils import HfHubHTTPError

from app.services.video.base import VideoProvider
from app.models.generation import Generation
from app.schemas.common import GenerationStatus
from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import (
    HFConfigurationErrorException,
    HFAuthenticationErrorException,
    HFRateLimitedException,
    HFInsufficientCreditsException,
    HFModelUnavailableException,
    HFProviderUnavailableException,
    HFGenerationFailedException,
    HFInvalidResultException,
    HFTimeoutException,
)


# Module-level job status storage for in-flight/completed HF async tasks
_HF_JOBS: Dict[str, Dict[str, Any]] = {}


class HuggingFaceVideoProvider(VideoProvider):
    """
    Hugging Face Inference Providers Text-to-Video Provider implementation.
    Default Model: Wan-AI/Wan2.2-TI2V-5B (or configured model)
    Default Provider: fal-ai (or configured inference provider routing)
    """

    def __init__(
        self,
        token: Optional[str] = None,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        timeout_seconds: float = 120.0,
    ):
        self.token = token if token is not None else settings.HF_TOKEN
        self.model = model or settings.HF_VIDEO_MODEL
        self.provider = provider or settings.HF_INFERENCE_PROVIDER or "fal-ai"
        self.timeout_seconds = timeout_seconds

    def _get_client(self) -> InferenceClient:
        if not self.token or not self.token.strip() or self.token.strip() == "your_huggingface_token_here":
            raise HFConfigurationErrorException("HF_TOKEN is not configured in backend/.env")
        return InferenceClient(
            token=self.token.strip(),
            provider=self.provider,
            timeout=self.timeout_seconds
        )

    async def submit_generation(self, generation: Generation) -> str:
        # Pre-validate token configuration before starting task
        client = self._get_client()

        job_id = f"hf-job-{uuid.uuid4().hex[:8]}"
        _HF_JOBS[job_id] = {
            "status": GenerationStatus.GENERATING,
            "progress": 30,
            "generation_id": generation.id,
            "result": None,
            "error": None,
        }

        prompt_to_use = generation.enhanced_prompt or generation.original_prompt
        negative_prompt = [generation.negative_prompt] if generation.negative_prompt else None

        logger.info(f"Submitting generation '{generation.id}' to Hugging Face provider '{self.provider}', model '{self.model}' (job_id='{job_id}')")

        # Execute remote inference asynchronously in thread pool
        asyncio.create_task(
            self._execute_hf_inference(
                client=client,
                generation_id=generation.id,
                job_id=job_id,
                prompt=prompt_to_use,
                negative_prompt=negative_prompt
            )
        )

        return job_id

    async def _execute_hf_inference(
        self,
        client: InferenceClient,
        generation_id: str,
        job_id: str,
        prompt: str,
        negative_prompt: Optional[list] = None
    ):
        start_time = time.time()
        try:
            # Run blocking InferenceClient.text_to_video in executor thread
            def _call_hf():
                kwargs = {
                    "prompt": prompt,
                    "model": self.model,
                }
                if negative_prompt:
                    kwargs["negative_prompt"] = negative_prompt
                return client.text_to_video(**kwargs)

            video_bytes = await asyncio.to_thread(_call_hf)

            if not video_bytes or not isinstance(video_bytes, bytes) or len(video_bytes) == 0:
                raise HFInvalidResultException("Hugging Face API returned empty or non-bytes payload")

            # Store generated video bytes safely under backend/generated/
            generated_dir = os.path.abspath(os.path.join(os.getcwd(), "generated"))
            os.makedirs(generated_dir, exist_ok=True)

            filename = f"moviq_{generation_id}.mp4"
            filepath = os.path.abspath(os.path.join(generated_dir, filename))

            with open(filepath, "wb") as f:
                f.write(video_bytes)

            if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
                raise HFInvalidResultException("Saved video MP4 is empty or invalid")

            elapsed = round(time.time() - start_time, 2)
            logger.info(f"Hugging Face video rendered successfully ({len(video_bytes)} bytes in {elapsed}s): {filepath}")

            _HF_JOBS[job_id]["status"] = GenerationStatus.COMPLETED
            _HF_JOBS[job_id]["progress"] = 100
            _HF_JOBS[job_id]["result"] = {
                "video_url": f"/api/v1/generations/{generation_id}/video",
                "thumbnail_url": "https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?auto=format&fit=crop&w=1200&q=80",
                "generation_time_seconds": elapsed
            }

        except HfHubHTTPError as err:
            status_code = getattr(err.response, "status_code", 500)
            err_text = getattr(err.response, "text", str(err))
            err_text_lower = err_text.lower()
            logger.error(f"Hugging Face HTTP error ({status_code}): {err_text}")
            
            if status_code in (401, 403):
                if "credit" in err_text_lower or "payment" in err_text_lower or "quota" in err_text_lower or "depleted" in err_text_lower:
                    exc = HFInsufficientCreditsException(f"Hugging Face account credits depleted or insufficient: {err_text}")
                else:
                    exc = HFAuthenticationErrorException(f"Hugging Face API token authentication failed: {err_text}")
            elif status_code == 402:
                exc = HFInsufficientCreditsException(f"Hugging Face account credits depleted: {err_text}")
            elif status_code == 422:
                exc = HFGenerationFailedException(f"Hugging Face provider parameters unprocessable (HTTP 422): {err_text}")
            elif status_code == 429:
                exc = HFRateLimitedException("Hugging Face API rate limit exceeded")
            elif status_code in (404, 503):
                exc = HFModelUnavailableException(f"Model '{self.model}' or provider '{self.provider}' unavailable: {err_text}")
            else:
                exc = HFGenerationFailedException(f"Hugging Face HTTP {status_code}: {err_text}")

            _HF_JOBS[job_id]["status"] = GenerationStatus.FAILED
            _HF_JOBS[job_id]["error"] = exc

        except (ValueError, StopIteration) as err:
            logger.error(f"Hugging Face provider mapping error: {err}")
            exc = HFModelUnavailableException(f"Model '{self.model}' is not supported by Hugging Face provider routing '{self.provider}'. {err}")
            _HF_JOBS[job_id]["status"] = GenerationStatus.FAILED
            _HF_JOBS[job_id]["error"] = exc

        except Exception as err:
            logger.error(f"Unexpected error executing Hugging Face inference for job '{job_id}': {err}")
            _HF_JOBS[job_id]["status"] = GenerationStatus.FAILED
            _HF_JOBS[job_id]["error"] = HFGenerationFailedException(str(err))

    async def check_status(self, provider_job_id: str) -> Tuple[GenerationStatus, Optional[int]]:
        job = _HF_JOBS.get(provider_job_id)
        if not job:
            return GenerationStatus.GENERATING, 50

        if job["status"] == GenerationStatus.FAILED and job.get("error"):
            raise job["error"]

        return job["status"], job.get("progress", 50)

    async def get_result(self, provider_job_id: str) -> Dict[str, Any]:
        job = _HF_JOBS.get(provider_job_id)
        if not job or not job.get("result"):
            raise HFInvalidResultException("No result available for Hugging Face job")
        return job["result"]
