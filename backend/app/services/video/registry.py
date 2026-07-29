from typing import List, Optional
from app.schemas.model_capability import ModelCapability
from app.schemas.common import AspectRatio, Duration
from app.core.exceptions import ModelNotFoundException


MOCK_MODELS: List[ModelCapability] = [
    ModelCapability(
        id="hunyuan-video-v1",
        name="Moviq Core (Hunyuan-Video)",
        provider="fal-ai",
        tag="Fast & High Fidelity",
        description="High-speed open video model with anamorphic depth controls.",
        supported_aspect_ratios=[AspectRatio.SIXTEEN_NINE, AspectRatio.NINE_SIXTEEN, AspectRatio.ONE_ONE],
        supported_durations=[Duration.FIVE_S, Duration.TEN_S],
        supports_negative_prompt=True,
        max_duration_seconds=10,
        is_available=True
    ),
    ModelCapability(
        id="fal-ai/kling-video/v2.5-turbo/pro/text-to-video",
        name="Kling 2.5 Turbo Pro",
        provider="fal-ai",
        tag="Production Cinematic",
        description="State-of-the-art text-to-video synthesis engine via fal-ai queue.",
        supported_aspect_ratios=[AspectRatio.SIXTEEN_NINE, AspectRatio.NINE_SIXTEEN, AspectRatio.ONE_ONE],
        supported_durations=[Duration.FIVE_S, Duration.TEN_S],
        supports_negative_prompt=True,
        max_duration_seconds=10,
        is_available=True
    ),
    ModelCapability(
        id="luma-dream-machine",
        name="Dream Machine v2.5",
        provider="luma-ai",
        tag="Ultra Dynamic Motion",
        description="Physics-informed realistic motion engine with high coherence.",
        supported_aspect_ratios=[AspectRatio.SIXTEEN_NINE, AspectRatio.NINE_SIXTEEN],
        supported_durations=[Duration.FIVE_S, Duration.TEN_S],
        supports_negative_prompt=False,
        max_duration_seconds=10,
        is_available=True
    ),
    ModelCapability(
        id="runway-gen3-alpha",
        name="Gen-3 Alpha Turbo",
        provider="runway",
        tag="Cinematic Framing",
        description="Industry standard video generation with extended 15s clips.",
        supported_aspect_ratios=[AspectRatio.SIXTEEN_NINE, AspectRatio.NINE_SIXTEEN, AspectRatio.ONE_ONE],
        supported_durations=[Duration.FIVE_S, Duration.TEN_S, Duration.FIFTEEN_S],
        supports_negative_prompt=True,
        max_duration_seconds=15,
        is_available=True
    ),
    ModelCapability(
        id="pika-v2.0",
        name="Pika 2.0 Motion",
        provider="pika-labs",
        tag="Stylized Realism",
        description="Specialized stylized rendering for anime and artistic video.",
        supported_aspect_ratios=[AspectRatio.SIXTEEN_NINE, AspectRatio.ONE_ONE],
        supported_durations=[Duration.FIVE_S],
        supports_negative_prompt=True,
        max_duration_seconds=5,
        is_available=True
    ),
    ModelCapability(
        id="Lightricks/LTX-Video",
        name="LTX-Video (Hugging Face)",
        provider="huggingface",
        tag="Zero-Cost Open Source",
        description="Fast open-source text-to-video model hosted on Hugging Face Inference Providers.",
        supported_aspect_ratios=[AspectRatio.SIXTEEN_NINE, AspectRatio.ONE_ONE],
        supported_durations=[Duration.FIVE_S],
        supports_negative_prompt=True,
        max_duration_seconds=5,
        is_available=True
    ),
    ModelCapability(
        id="Wan-AI/Wan2.1-T2V-1.3B-Diffusers",
        name="Wan2.1 T2V 1.3B",
        provider="wan",
        tag="Open Source / Local GPU",
        description="Open-source text-to-video model validated on a Tesla P100 GPU (576x320, 33 frames).",
        supported_aspect_ratios=[AspectRatio.SIXTEEN_NINE, AspectRatio.ONE_ONE],
        supported_durations=[Duration.FIVE_S],
        supports_negative_prompt=True,
        max_duration_seconds=5,
        render_profile_description="576×320 | 33 frames @ 16 FPS (~2.06s render)",
        is_available=True
    )
]


def get_all_models() -> List[ModelCapability]:
    return MOCK_MODELS


def get_model_capability(model_id: str) -> ModelCapability:
    for model in MOCK_MODELS:
        if model.id == model_id:
            return model
    raise ModelNotFoundException(model_id)
