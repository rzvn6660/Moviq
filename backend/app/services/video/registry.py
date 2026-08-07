import os
from typing import List, Optional
from app.schemas.model_capability import ModelCapability, ExecutionMode
from app.schemas.common import AspectRatio, Duration
from app.core.exceptions import ModelNotFoundException
from app.core.config import settings


RAW_MODEL_DEFINITIONS: List[dict] = [
    {
        "id": "kling-3.0/video",
        "name": "Kling 3.0 Pro (Kie.ai)",
        "provider": "kie",
        "execution_mode": ExecutionMode.HOSTED_API,
        "tag": "Production Hosted",
        "description": "State-of-the-art cinematic text-to-video model routed via Kie.ai unified provider.",
        "supported_aspect_ratios": [AspectRatio.SIXTEEN_NINE, AspectRatio.NINE_SIXTEEN, AspectRatio.ONE_ONE],
        "supported_durations": [Duration.FIVE_S, Duration.TEN_S],
        "supports_negative_prompt": True,
        "max_duration_seconds": 10,
    },
    {
        "id": "wan-2.1/video",
        "name": "Wan 2.1 T2V (Kie.ai)",
        "provider": "kie",
        "execution_mode": ExecutionMode.HOSTED_API,
        "tag": "Production Hosted",
        "description": "High-fidelity open text-to-video model hosted on Kie.ai backend.",
        "supported_aspect_ratios": [AspectRatio.SIXTEEN_NINE, AspectRatio.ONE_ONE],
        "supported_durations": [Duration.FIVE_S],
        "supports_negative_prompt": True,
        "max_duration_seconds": 5,
    },
    {
        "id": "veo-3.1",
        "name": "Google Veo 3.1 (Kie.ai)",
        "provider": "kie",
        "execution_mode": ExecutionMode.HOSTED_API,
        "tag": "Cinematic Ultra",
        "description": "Google Veo 3.1 1080p photorealistic video generation via Kie.ai.",
        "supported_aspect_ratios": [AspectRatio.SIXTEEN_NINE, AspectRatio.NINE_SIXTEEN, AspectRatio.ONE_ONE],
        "supported_durations": [Duration.FIVE_S, Duration.TEN_S],
        "supports_negative_prompt": False,
        "max_duration_seconds": 10,
    },
    {
        "id": "dream-machine",
        "name": "Dream Machine (Luma AI)",
        "provider": "luma",
        "execution_mode": ExecutionMode.HOSTED_API,
        "tag": "Luma Engine",
        "description": "Physics-informed realistic camera motion engine via Luma AI REST API.",
        "supported_aspect_ratios": [AspectRatio.SIXTEEN_NINE, AspectRatio.NINE_SIXTEEN, AspectRatio.ONE_ONE],
        "supported_durations": [Duration.FIVE_S],
        "supports_negative_prompt": False,
        "max_duration_seconds": 5,
    },
    {
        "id": "hailuo-01",
        "name": "MiniMax Video 01 (Hailuo AI)",
        "provider": "hailuo",
        "execution_mode": ExecutionMode.HOSTED_API,
        "tag": "MiniMax Engine",
        "description": "MiniMax Hailuo high-motion synthesis engine via MiniMax REST API.",
        "supported_aspect_ratios": [AspectRatio.SIXTEEN_NINE, AspectRatio.NINE_SIXTEEN, AspectRatio.ONE_ONE],
        "supported_durations": [Duration.FIVE_S],
        "supports_negative_prompt": True,
        "max_duration_seconds": 6,
    },
    {
        "id": "Wan-AI/Wan2.2-TI2V-5B",
        "name": "Wan2.2 TI2V 5B (Hugging Face)",
        "provider": "huggingface",
        "execution_mode": ExecutionMode.HOSTED_INFERENCE,
        "tag": "Hosted Inference",
        "description": "Hosted serverless text-to-video model routing via Hugging Face Inference API.",
        "supported_aspect_ratios": [AspectRatio.SIXTEEN_NINE, AspectRatio.ONE_ONE],
        "supported_durations": [Duration.FIVE_S],
        "supports_negative_prompt": True,
        "max_duration_seconds": 5,
    },
    {
        "id": "Wan-AI/Wan2.1-T2V-1.3B-Diffusers",
        "name": "Wan2.1 T2V 1.3B (Remote GPU)",
        "provider": "remote_wan",
        "execution_mode": ExecutionMode.SELF_HOSTED,
        "tag": "Self-Hosted GPU",
        "description": "Open-source text-to-video model for self-hosted CUDA GPU workers (576x320, 33 frames).",
        "supported_aspect_ratios": [AspectRatio.SIXTEEN_NINE, AspectRatio.ONE_ONE],
        "supported_durations": [Duration.FIVE_S],
        "supports_negative_prompt": True,
        "max_duration_seconds": 5,
        "render_profile_description": "576×320 | 33 frames @ 16 FPS (~2.06s render)",
    },
    {
        "id": "ltx-video",
        "name": "LTX Video 0.9 (Lightricks Local)",
        "provider": "ltx",
        "execution_mode": ExecutionMode.SELF_HOSTED,
        "tag": "Local Inference",
        "description": "Local PyTorch real-time video diffusion engine.",
        "supported_aspect_ratios": [AspectRatio.SIXTEEN_NINE, AspectRatio.NINE_SIXTEEN, AspectRatio.ONE_ONE],
        "supported_durations": [Duration.FIVE_S],
        "supports_negative_prompt": True,
        "max_duration_seconds": 5,
    }
]


def get_all_models() -> List[ModelCapability]:
    is_mock_mode = settings.VIDEO_PROVIDER.lower() == "mock"

    models = []
    for raw in RAW_MODEL_DEFINITIONS:
        m = ModelCapability(**raw)

        if is_mock_mode:
            m.configured = True
            m.is_available = True
            m.status_label = "READY"
        else:
            # Dynamic runtime configuration evaluation for v2.0 real execution
            if m.provider == "kie":
                key_valid = bool(
                    settings.KIE_API_KEY
                    and settings.KIE_API_KEY.strip()
                    and settings.KIE_API_KEY != "your_kie_api_key_here"
                )
                m.configured = key_valid
                m.is_available = key_valid
                m.status_label = "READY" if key_valid else "NOT AVAILABLE"

            elif m.provider == "luma":
                luma_key = os.getenv("LUMA_API_KEY") or getattr(settings, "LUMA_API_KEY", "")
                key_valid = bool(luma_key and luma_key.strip())
                m.configured = key_valid
                m.is_available = key_valid
                m.status_label = "READY" if key_valid else "NOT AVAILABLE"

            elif m.provider == "hailuo":
                hailuo_key = os.getenv("HAILUO_API_KEY") or os.getenv("MINIMAX_API_KEY") or getattr(settings, "HAILUO_API_KEY", "")
                key_valid = bool(hailuo_key and hailuo_key.strip())
                m.configured = key_valid
                m.is_available = key_valid
                m.status_label = "READY" if key_valid else "NOT AVAILABLE"

            elif m.provider == "huggingface":
                token_valid = bool(
                    settings.HF_TOKEN
                    and settings.HF_TOKEN.strip()
                    and settings.HF_TOKEN != "your_huggingface_token_here"
                )
                m.configured = token_valid
                m.is_available = token_valid
                m.status_label = "READY" if token_valid else "NOT AVAILABLE"

            elif m.provider == "remote_wan":
                url_valid = bool(
                    settings.REMOTE_WAN_URL
                    and settings.REMOTE_WAN_URL.strip()
                    and settings.REMOTE_WAN_URL != "http://localhost:8002"
                )
                is_ready = url_valid
                m.configured = is_ready
                m.is_available = is_ready
                m.status_label = "READY" if is_ready else "NOT AVAILABLE"

            elif m.provider == "ltx":
                # LTX is ready locally if PyTorch/CUDA or synthetic fallback mode is active
                m.configured = True
                m.is_available = True
                m.status_label = "READY"

            else:
                m.configured = False
                m.is_available = False
                m.status_label = "NOT AVAILABLE"

        models.append(m)

    return models


def get_model_capability(model_id: str) -> ModelCapability:
    for model in get_all_models():
        if model.id == model_id:
            return model
    raise ModelNotFoundException(model_id)
