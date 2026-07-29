import pytest
from app.services.video.registry import get_all_models, get_model_capability
from app.services.video.factory import get_video_provider
from app.services.video.huggingface import HuggingFaceVideoProvider
from app.services.video.remote_wan import RemoteWanVideoProvider
from app.core.config import settings
from app.core.exceptions import ProviderFailureException
from app.schemas.generation import CreateGenerationRequest
from app.services.generation_service import GenerationService


def test_registry_truthful_configuration_metadata():
    original_provider = settings.VIDEO_PROVIDER
    settings.VIDEO_PROVIDER = "huggingface"

    models = get_all_models()
    model_ids = [m.id for m in models]
    assert "Wan-AI/Wan2.2-TI2V-5B" in model_ids
    assert "luma-dream-machine" in model_ids
    assert "pika-v2.0" in model_ids

    # Unconfigured proprietary model must report configured=False and status_label="NOT CONFIGURED"
    luma = get_model_capability("luma-dream-machine")
    assert luma.configured is False
    assert luma.is_available is False
    assert luma.status_label == "NOT CONFIGURED"
    assert luma.external_url == "https://lumalabs.ai/dream-machine"

    settings.VIDEO_PROVIDER = original_provider


def test_dynamic_factory_model_routing():
    original_provider = settings.VIDEO_PROVIDER
    settings.VIDEO_PROVIDER = "huggingface"

    # 1. Route Wan2.2 -> HuggingFaceVideoProvider
    p_hf = get_video_provider("Wan-AI/Wan2.2-TI2V-5B")
    assert isinstance(p_hf, HuggingFaceVideoProvider)
    assert p_hf.model == "Wan-AI/Wan2.2-TI2V-5B"

    # 2. Route Wan2.1 -> RemoteWanVideoProvider
    p_wan = get_video_provider("Wan-AI/Wan2.1-T2V-1.3B-Diffusers")
    assert isinstance(p_wan, RemoteWanVideoProvider)

    settings.VIDEO_PROVIDER = original_provider


def test_unconfigured_model_rejection_no_mock_fallback():
    original_provider = settings.VIDEO_PROVIDER
    settings.VIDEO_PROVIDER = "huggingface"

    with pytest.raises(ProviderFailureException) as exc_info:
        get_video_provider("pika-v2.0")

    assert "unconfigured or unavailable" in str(exc_info.value).lower()

    settings.VIDEO_PROVIDER = original_provider


@pytest.mark.asyncio
async def test_generation_service_persists_execution_mode(db_session):
    original_provider = settings.VIDEO_PROVIDER
    settings.VIDEO_PROVIDER = "huggingface"

    service = GenerationService(db_session)
    req = CreateGenerationRequest(
        prompt="A futuristic sports car drifting through neon rain",
        modelId="Wan-AI/Wan2.2-TI2V-5B",
        aspectRatio="16:9",
        duration="5s"
    )

    res = await service.create_generation(req)
    assert res.id.startswith("moviq-gen-")

    gen = service.repository.get_by_id(res.id)
    assert gen.model_id == "Wan-AI/Wan2.2-TI2V-5B"
    assert gen.execution_mode == "Hosted Inference"

    settings.VIDEO_PROVIDER = original_provider
