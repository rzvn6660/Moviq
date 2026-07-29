import os
import uuid
import time
import asyncio
from typing import Tuple, Optional, Dict, Any

from app.services.video.base import VideoProvider
from app.models.generation import Generation
from app.schemas.common import GenerationStatus
from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import (
    WANDependenciesMissingException,
    WANCUDAUnavailableException,
    WANModelLoadFailedException,
    WANOutOfMemoryException,
    WANGenerationFailedException,
    WANInvalidOutputException,
)


# Module-level job status storage for in-flight Wan2.1 inference tasks
_WAN_JOBS: Dict[str, Dict[str, Any]] = {}


class WanVideoProvider(VideoProvider):
    """
    Wan2.1 T2V 1.3B Open-Source Video Provider.
    Model: Wan-AI/Wan2.1-T2V-1.3B-Diffusers
    Lazy-loads heavy PyTorch / Diffusers ML stack only during active inference.
    """

    def __init__(
        self,
        model_id: Optional[str] = None,
        device: Optional[str] = None,
        dtype: Optional[str] = None,
        num_inference_steps: Optional[int] = None,
        guidance_scale: Optional[float] = None,
        fps: Optional[int] = None,
    ):
        self.model_id = model_id or settings.WAN_MODEL_ID
        self.device = device or settings.WAN_DEVICE
        self.dtype = dtype or settings.WAN_DTYPE
        self.num_inference_steps = num_inference_steps or settings.WAN_NUM_INFERENCE_STEPS
        self.guidance_scale = guidance_scale or settings.WAN_GUIDANCE_SCALE
        self.fps = fps or settings.WAN_FPS

    def _ensure_ml_dependencies_and_cuda(self):
        """
        Lazy-loads PyTorch and Diffusers dependencies dynamically.
        Ensures normal FastAPI server startup requires ZERO heavy ML packages installed.
        """
        try:
            import torch
            import diffusers
            import transformers
        except ImportError as err:
            logger.error(f"Wan2.1 dependencies missing: {err}")
            raise WANDependenciesMissingException()

        import torch
        if not torch.cuda.is_available():
            logger.error("Wan2.1 requested but CUDA GPU is unavailable")
            raise WANCUDAUnavailableException()

    async def submit_generation(self, generation: Generation) -> str:
        # Pre-validate dependencies & CUDA availability before creating task
        self._ensure_ml_dependencies_and_cuda()

        job_id = f"wan-job-{uuid.uuid4().hex[:8]}"
        _WAN_JOBS[job_id] = {
            "status": GenerationStatus.GENERATING,
            "progress": 30,
            "generation_id": generation.id,
            "result": None,
            "error": None,
        }

        prompt_to_use = generation.enhanced_prompt or generation.original_prompt
        negative_prompt = generation.negative_prompt

        logger.info(f"Submitting generation '{generation.id}' to local Wan2.1 GPU engine (job_id='{job_id}')")

        # Spawn asynchronous inference worker in thread executor
        asyncio.create_task(
            self._execute_wan_inference(
                generation_id=generation.id,
                job_id=job_id,
                prompt=prompt_to_use,
                negative_prompt=negative_prompt
            )
        )

        return job_id

    async def _execute_wan_inference(
        self,
        generation_id: str,
        job_id: str,
        prompt: str,
        negative_prompt: Optional[str] = None
    ):
        start_time = time.time()
        try:
            def _run_diffusers_wan():
                import torch
                from diffusers import WanPipeline
                from diffusers.utils import export_to_video

                torch_dtype = torch.float16 if self.dtype == "float16" else torch.float32

                logger.info(f"Loading Wan2.1 pipeline weights '{self.model_id}' ({self.dtype})...")
                pipe = WanPipeline.from_pretrained(
                    self.model_id,
                    torch_dtype=torch_dtype
                )

                # Memory optimization for 16GB GPUs (Tesla P100)
                pipe.enable_model_cpu_offload()
                pipe.enable_vae_tiling()

                logger.info("Executing Wan2.1 diffusion loop (576x320, 33 frames, 20 steps)...")
                kwargs = {
                    "prompt": prompt,
                    "height": 320,
                    "width": 576,
                    "num_frames": 33,
                    "num_inference_steps": self.num_inference_steps,
                    "guidance_scale": self.guidance_scale,
                }
                if negative_prompt:
                    kwargs["negative_prompt"] = negative_prompt

                output = pipe(**kwargs)
                frames = output.frames[0]

                generated_dir = os.path.join(os.getcwd(), "generated")
                os.makedirs(generated_dir, exist_ok=True)
                filepath = os.path.join(generated_dir, f"moviq_{generation_id}.mp4")

                export_to_video(frames, filepath, fps=self.fps)
                return filepath

            filepath = await asyncio.to_thread(_run_diffusers_wan)

            if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
                raise WANInvalidOutputException("Wan2.1 exported video file is empty or missing")

            elapsed = round(time.time() - start_time, 2)
            logger.info(f"Wan2.1 video rendered successfully in {elapsed}s: {filepath}")

            _WAN_JOBS[job_id]["status"] = GenerationStatus.COMPLETED
            _WAN_JOBS[job_id]["progress"] = 100
            _WAN_JOBS[job_id]["result"] = {
                "video_url": f"/api/v1/generations/{generation_id}/video",
                "thumbnail_url": "https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?auto=format&fit=crop&w=1200&q=80",
                "generation_time_seconds": elapsed
            }

        except Exception as err:
            err_str = str(err)
            logger.error(f"Wan2.1 inference failed for job '{job_id}': {err}")

            if "out of memory" in err_str.lower() or "oom" in err_str.lower():
                exc = WANOutOfMemoryException(f"CUDA Out of Memory: {err}")
            elif "load" in err_str.lower() or "checkpoint" in err_str.lower():
                exc = WANModelLoadFailedException(f"Model load error: {err}")
            elif isinstance(err, (WANInvalidOutputException, WANDependenciesMissingException, WANCUDAUnavailableException)):
                exc = err
            else:
                exc = WANGenerationFailedException(err_str)

            _WAN_JOBS[job_id]["status"] = GenerationStatus.FAILED
            _WAN_JOBS[job_id]["error"] = exc

    async def check_status(self, provider_job_id: str) -> Tuple[GenerationStatus, Optional[int]]:
        job = _WAN_JOBS.get(provider_job_id)
        if not job:
            return GenerationStatus.GENERATING, 50

        if job["status"] == GenerationStatus.FAILED and job.get("error"):
            raise job["error"]

        return job["status"], job.get("progress", 50)

    async def get_result(self, provider_job_id: str) -> Dict[str, Any]:
        job = _WAN_JOBS.get(provider_job_id)
        if not job or not job.get("result"):
            raise WANInvalidOutputException("No valid result found for Wan2.1 job")
        return job["result"]
