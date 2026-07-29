from typing import List, Optional
from app.schemas.model_capability import ModelCapability, ExecutionMode
from app.schemas.common import AspectRatio, Duration
from app.core.exceptions import ModelNotFoundException
from app.core.config import settings


RAW_MODEL_DEFINITIONS: List[dict] = [
    {
        "id": "Wan-AI/Wan2.2-TI2V-5B",
        "name": "Wan2.2 TI2V 5B (Hugging Face)",
        "provider": "huggingface",
        "execution_mode": ExecutionMode.HOSTED_INFERENCE,
        "tag": "Hosted Inference",
        "description": "Hosted serverless text-to-video model routing via Hugging Face Inference API (fal-ai provider).",
        "supported_aspect_ratios": [AspectRatio.SIXTEEN_NINE, AspectRatio.ONE_ONE],
        "supported_durations": [Duration.FIVE_S],
        "supports_negative_prompt": True,
        "max_duration_seconds": 5,
    },
    {
        "id": "hunyuan-video-v1",
        "name": "Moviq Core (Hunyuan-Video)",
        "provider": "fal-ai",
        "execution_mode": ExecutionMode.HOSTED_API,
        "tag": "Hosted Cloud Queue",
        "description": "High-speed open video model with anamorphic depth controls.",
        "supported_aspect_ratios": [AspectRatio.SIXTEEN_NINE, AspectRatio.NINE_SIXTEEN, AspectRatio.ONE_ONE],
        "supported_durations": [Duration.FIVE_S, Duration.TEN_S],
        "supports_negative_prompt": True,
        "max_duration_seconds": 10,
    },
    {
        "id": "Wan-AI/Wan2.1-T2V-1.3B-Diffusers",
        "name": "Wan2.1 T2V 1.3B",
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
        "id": "fal-ai/kling-video/v2.5-turbo/pro/text-to-video",
        "name": "Kling 2.5 Turbo Pro",
        "provider": "fal-ai",
        "execution_mode": ExecutionMode.HOSTED_API,
        "tag": "Production Cinematic",
        "description": "State-of-the-art text-to-video synthesis engine via fal-ai queue.",
        "supported_aspect_ratios": [AspectRatio.SIXTEEN_NINE, AspectRatio.NINE_SIXTEEN, AspectRatio.ONE_ONE],
        "supported_durations": [Duration.FIVE_S, Duration.TEN_S],
        "supports_negative_prompt": True,
        "max_duration_seconds": 10,
    },
    {
        "id": "luma-dream-machine",
        "name": "Dream Machine v2.5",
        "provider": "luma-ai",
        "execution_mode": ExecutionMode.EXTERNAL_WEB,
        "tag": "External API",
        "description": "Physics-informed realistic motion engine capability.",
        "supported_aspect_ratios": [AspectRatio.SIXTEEN_NINE, AspectRatio.NINE_SIXTEEN],
        "supported_durations": [Duration.FIVE_S, Duration.TEN_S],
        "supports_negative_prompt": False,
        "max_duration_seconds": 10,
        "external_url": "https://lumalabs.ai/dream-machine",
    },
    {
        "id": "runway-gen3-alpha",
        "name": "Gen-3 Alpha Turbo",
        "provider": "runway",
        "execution_mode": ExecutionMode.EXTERNAL_WEB,
        "tag": "External API",
        "description": "Industry standard video generation capability.",
        "supported_aspect_ratios": [AspectRatio.SIXTEEN_NINE, AspectRatio.NINE_SIXTEEN, AspectRatio.ONE_ONE],
        "supported_durations": [Duration.FIVE_S, Duration.TEN_S, Duration.FIFTEEN_S],
        "supports_negative_prompt": True,
        "max_duration_seconds": 15,
        "external_url": "https://runwayml.com",
    },
    {
        "id": "pika-v2.0",
        "name": "Pika 2.0 Motion",
        "provider": "pika-labs",
        "execution_mode": ExecutionMode.EXTERNAL_WEB,
        "tag": "External API",
        "description": "Specialized stylized video rendering engine.",
        "supported_aspect_ratios": [AspectRatio.SIXTEEN_NINE, AspectRatio.ONE_ONE],
        "supported_durations": [Duration.FIVE_S],
        "supports_negative_prompt": True,
        "max_duration_seconds": 5,
        "external_url": "https://pika.art",
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
            # Dynamic runtime configuration evaluation for real execution
            if m.provider == "huggingface":
                token_valid = bool(
                    settings.HF_TOKEN
                    and settings.HF_TOKEN.strip()
                    and settings.HF_TOKEN != "your_huggingface_token_here"
                )
                m.configured = token_valid
                m.is_available = token_valid
                m.status_label = "READY" if token_valid else "NOT CONFIGURED"

            elif m.provider == "fal-ai":
                key_valid = bool(
                    settings.FAL_KEY
                    and settings.FAL_KEY.strip()
                    and settings.FAL_KEY != "your_fal_api_key_here"
                )
                m.configured = key_valid
                m.is_available = key_valid
                m.status_label = "READY" if key_valid else "NOT CONFIGURED"

            elif m.provider in ("remote_wan", "wan"):
                url_valid = bool(
                    settings.REMOTE_WAN_URL
                    and settings.REMOTE_WAN_URL.strip()
                    and settings.REMOTE_WAN_URL != "http://localhost:8002"
                )
                key_valid = bool(
                    settings.REMOTE_WAN_API_KEY
                    and settings.REMOTE_WAN_API_KEY.strip()
                    and settings.REMOTE_WAN_API_KEY != "your_remote_wan_api_key_here"
                )
                is_ready = url_valid and key_valid
                m.configured = is_ready
                m.is_available = is_ready
                m.status_label = "READY" if is_ready else "NOT CONFIGURED"

            else:
                m.configured = False
                m.is_available = False
                m.status_label = "NOT CONFIGURED"

        models.append(m)

    return models


def get_model_capability(model_id: str) -> ModelCapability:
    for model in get_all_models():
        if model.id == model_id:
            return model
    raise ModelNotFoundException(model_id)
