import pytest
from app.services.video.registry import get_all_models, get_model_capability
from app.services.video.factory import get_video_provider
from app.services.video.luma import LumaVideoProvider
from app.services.video.hailuo import HailuoVideoProvider
from app.services.video.ltx import LTXVideoProvider
from app.services.video.huggingface import HuggingFaceVideoProvider
from app.services.video.remote_wan import RemoteWanVideoProvider
from app.services.video.kie import KieVideoProvider
from app.core.config import settings
from app.core.exceptions import ModelNotFoundException
from app.schemas.generation import CreateGenerationRequest
from app.services.generation_service import GenerationService


def test_registry_v2_provider_matrix():
    models = get_all_models()
    model_ids = [m.id for m in models]
    assert "kling-3.0/video" in model_ids
    assert "dream-machine" in model_ids
    assert "hailuo-01" in model_ids
    assert "Wan-AI/Wan2.2-TI2V-5B" in model_ids
    assert "Wan-AI/Wan2.1-T2V-1.3B-Diffusers" in model_ids
    assert "ltx-video" in model_ids


def test_dynamic_factory_model_routing_v2():
    original_provider = settings.VIDEO_PROVIDER
    settings.VIDEO_PROVIDER = "kie"

    # 1. Route dream-machine -> LumaVideoProvider
    p_luma = get_video_provider("dream-machine")
    assert isinstance(p_luma, LumaVideoProvider)

    # 2. Route hailuo-01 -> HailuoVideoProvider
    p_hailuo = get_video_provider("hailuo-01")
    assert isinstance(p_hailuo, HailuoVideoProvider)

    # 3. Route ltx-video -> LTXVideoProvider
    p_ltx = get_video_provider("ltx-video")
    assert isinstance(p_ltx, LTXVideoProvider)

    # 4. Route Wan2.2 -> HuggingFaceVideoProvider
    p_hf = get_video_provider("Wan-AI/Wan2.2-TI2V-5B")
    assert isinstance(p_hf, HuggingFaceVideoProvider)

    # 5. Route Wan2.1 -> RemoteWanVideoProvider
    p_wan = get_video_provider("Wan-AI/Wan2.1-T2V-1.3B-Diffusers")
    assert isinstance(p_wan, RemoteWanVideoProvider)

    settings.VIDEO_PROVIDER = original_provider


def test_unsupported_model_rejection():
    with pytest.raises(ModelNotFoundException):
        get_model_capability("non-existent-model")


@pytest.mark.asyncio
async def test_generation_service_persists_v2_provider_execution_mode(db_session):
    original_provider = settings.VIDEO_PROVIDER
    old_synth = settings.ENABLE_SYNTHETIC_FALLBACK
    settings.VIDEO_PROVIDER = "kie"
    settings.ENABLE_SYNTHETIC_FALLBACK = True

    service = GenerationService(db_session)
    req = CreateGenerationRequest(
        prompt="A futuristic sports car drifting through neon rain",
        modelId="kling-3.0/video",
        aspectRatio="16:9",
        duration="5s"
    )

    res = await service.create_generation(req)
    assert res.id.startswith("moviq-gen-")

    gen = service.repository.get_by_id(res.id)
    assert gen.model_id == "kling-3.0/video"
    assert gen.provider == "kie"

    settings.VIDEO_PROVIDER = original_provider
