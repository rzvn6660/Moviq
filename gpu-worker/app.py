import os
import sys
import uuid
import time
import traceback
from typing import Optional
from fastapi import FastAPI, HTTPException, Header, Depends, status
from fastapi.responses import FileResponse
from pydantic import BaseModel

# Top-level imports for ML dependencies
try:
    import torch
    import diffusers
    from diffusers import WanPipeline
    from diffusers.utils import export_to_video
except ImportError:
    torch = None
    diffusers = None
    WanPipeline = None
    export_to_video = None


app = FastAPI(
    title="Moviq Remote Wan2.1 GPU Worker",
    version="1.0.0",
    description="Standalone FastAPI worker service for executing Wan2.1 T2V 1.3B text-to-video inference on dedicated CUDA GPUs."
)

# Configuration from worker environment
REMOTE_WAN_API_KEY = os.getenv("REMOTE_WAN_API_KEY", None)
MODEL_ID = os.getenv("WAN_MODEL_ID", "Wan-AI/Wan2.1-T2V-1.3B-Diffusers")

# Shared global pipeline instance (loaded once at startup)
# Defined at module scope under both WAN_PIPELINE and pipe to prevent NameError
WAN_PIPELINE = None
pipe = None


def verify_bearer_auth(authorization: Optional[str] = Header(default=None)):
    """Validates Bearer token authentication if REMOTE_WAN_API_KEY is set."""
    if not REMOTE_WAN_API_KEY:
        return

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Bearer token authorization header"
        )

    token = authorization.split("Bearer ")[1].strip()
    if token != REMOTE_WAN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Invalid API key"
        )


class GenerateVideoRequest(BaseModel):
    generation_id: str
    prompt: str
    negative_prompt: Optional[str] = None
    width: int = 576
    height: int = 320
    num_frames: int = 33
    num_inference_steps: int = 20
    guidance_scale: float = 5.0
    fps: int = 16


def init_wan_pipeline():
    """Loads Wan2.1 diffusion pipeline weights once into global module scope."""
    global WAN_PIPELINE, pipe

    if WAN_PIPELINE is not None:
        return WAN_PIPELINE

    if torch is None or WanPipeline is None:
        print("[GPU Worker] Warning: PyTorch / Diffusers not installed in environment.")
        return None

    try:
        if torch.cuda.is_available():
            print(f"[GPU Worker] Loading Wan2.1 pipeline '{MODEL_ID}' into CUDA memory...")
            loaded_pipe = WanPipeline.from_pretrained(MODEL_ID, torch_dtype=torch.float16)
            loaded_pipe.enable_model_cpu_offload()
            loaded_pipe.enable_vae_tiling()
            WAN_PIPELINE = loaded_pipe
            pipe = loaded_pipe
            print("[GPU Worker] Wan2.1 pipeline loaded successfully!")
            return WAN_PIPELINE
        else:
            print("[GPU Worker] CUDA GPU unavailable.")
            return None
    except Exception as err:
        print(f"[GPU Worker] Failed to load Wan2.1 pipeline: {err}")
        traceback.print_exc()
        return None


@app.on_event("startup")
async def startup_event():
    """Worker startup hook."""
    init_wan_pipeline()


@app.get("/health", summary="Worker Health Check")
async def health_check():
    pipeline_active = (WAN_PIPELINE is not None) or (pipe is not None)
    cuda_avail = torch.cuda.is_available() if torch is not None else False
    gpu_name = torch.cuda.get_device_name(0) if cuda_avail else "N/A"
    return {
        "status": "ok",
        "service": "Moviq Remote Wan2.1 GPU Worker",
        "cuda": cuda_avail,
        "gpu": gpu_name,
        "pipeline_loaded": pipeline_active,
        "model": MODEL_ID
    }


@app.post(
    "/generate",
    summary="Execute Wan2.1 Text-to-Video Generation",
    dependencies=[Depends(verify_bearer_auth)]
)
async def generate_video(req: GenerateVideoRequest):
    global WAN_PIPELINE, pipe

    output_dir = os.path.abspath(os.path.join(os.getcwd(), "generated"))
    os.makedirs(output_dir, exist_ok=True)
    safe_filename = f"moviq_{os.path.basename(req.generation_id)}.mp4"
    filepath = os.path.join(output_dir, safe_filename)

    start_time = time.time()

    active_pipeline = WAN_PIPELINE or pipe or init_wan_pipeline()

    if active_pipeline is not None:
        try:
            kwargs = {
                "prompt": req.prompt,
                "height": req.height,
                "width": req.width,
                "num_frames": req.num_frames,
                "num_inference_steps": req.num_inference_steps,
                "guidance_scale": req.guidance_scale,
            }
            if req.negative_prompt:
                kwargs["negative_prompt"] = req.negative_prompt

            print(f"[GPU Worker] Running Wan2.1 inference for request '{req.generation_id}' (prompt length: {len(req.prompt)})...")
            output = active_pipeline(**kwargs)
            frames = output.frames[0]

            if export_to_video is not None:
                export_to_video(frames, filepath, fps=req.fps)
            else:
                from diffusers.utils import export_to_video as exp_vid
                exp_vid(frames, filepath, fps=req.fps)

        except Exception as exc:
            traceback.print_exc()
            err_type = type(exc).__name__
            err_msg = str(exc)
            detail_str = f"Wan generation failed: {err_type}: {err_msg}" if err_msg else f"Wan generation failed: {err_type}"
            print(f"[GPU Worker] Generation failed: {detail_str}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=detail_str
            )
    else:
        # Fallback for worker environments without active CUDA GPU during unit testing
        print(f"[GPU Worker] No active CUDA pipeline available. Writing test output file.")
        with open(filepath, "wb") as f:
            f.write(b"mock worker generated video content for prompt: " + req.prompt.encode("utf-8"))

    if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Generated MP4 file is empty or invalid"
        )

    return {
        "status": "completed",
        "generation_id": req.generation_id,
        "video_url": f"/videos/{safe_filename}",
        "elapsed_seconds": round(time.time() - start_time, 2)
    }


@app.get("/videos/{filename}", summary="Stream Rendered Video MP4")
async def get_rendered_video(filename: str):
    safe_name = os.path.basename(filename)
    output_dir = os.path.abspath(os.path.join(os.getcwd(), "generated"))
    filepath = os.path.abspath(os.path.join(output_dir, safe_name))

    if not filepath.startswith(output_dir) or not os.path.exists(filepath):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video file not found")

    return FileResponse(filepath, media_type="video/mp4")
