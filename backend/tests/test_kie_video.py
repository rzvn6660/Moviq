import os
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import Response
from app.services.video.kie import KieVideoProvider
from app.services.video.registry import get_all_models, get_model_capability
from app.services.video.factory import get_video_provider
from app.models.generation import Generation
from app.schemas.common import GenerationStatus
from app.core.config import settings
from app.core.exceptions import (
    KieConfigurationErrorException,
    KieAuthenticationErrorException,
    KieRateLimitedException,
    KieQuotaExceededException,
    KieModelUnavailableException,
    KieProviderUnavailableException,
    KieGenerationFailedException,
    KieInvalidResultException,
)


@pytest.fixture
def sample_generation():
    return Generation(
        id="test-gen-kie-123",
        original_prompt="A red sports car racing down a neon street at night",
        enhanced_prompt="Cinematic tracking shot of a red sports car racing down a neon wet street at night",
        negative_prompt="blurry, distorted",
        aspect_ratio="16:9",
        duration="5s",
        model_id="kling-3.0/video",
        provider="kie",
    )


def test_kie_unconfigured_raises_exception():
    provider = KieVideoProvider(api_key="")
    with pytest.raises(KieConfigurationErrorException):
        provider._validate_config()


@pytest.mark.asyncio
async def test_kie_submit_generation_success(sample_generation):
    provider = KieVideoProvider(api_key="test_kie_key_123", base_url="https://api.kie.ai")

    mock_resp = Response(
        200,
        json={
            "code": 200,
            "msg": "success",
            "data": {"taskId": "kie-task-abc-789"}
        }
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp
        job_id = await provider.submit_generation(sample_generation)
        assert job_id.startswith("kie-job-")

        status, pct = await provider.check_status(job_id)
        assert status in [GenerationStatus.GENERATING, GenerationStatus.COMPLETED]


@pytest.mark.asyncio
async def test_kie_submit_generation_auth_error(sample_generation):
    orig_synth = settings.ENABLE_SYNTHETIC_FALLBACK
    orig_prov = settings.VIDEO_PROVIDER
    settings.ENABLE_SYNTHETIC_FALLBACK = False
    settings.VIDEO_PROVIDER = "kie"
    try:
        provider = KieVideoProvider(api_key="invalid_key", base_url="https://api.kie.ai")

        mock_resp = Response(401, json={"code": 401, "msg": "Unauthorized"})

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_resp
            with pytest.raises(KieAuthenticationErrorException):
                await provider.submit_generation(sample_generation)
    finally:
        settings.ENABLE_SYNTHETIC_FALLBACK = orig_synth
        settings.VIDEO_PROVIDER = orig_prov


@pytest.mark.asyncio
async def test_kie_status_polling_and_download_flow(sample_generation):
    provider = KieVideoProvider(api_key="test_kie_key_123", base_url="https://api.kie.ai")

    # Mock Task Creation Response
    create_resp = Response(
        200,
        json={"code": 200, "msg": "success", "data": {"taskId": "kie-task-456"}}
    )

    # Mock Task Status Poll Response -> Completed with Video URL
    video_cdn_url = "https://cdn.kie.ai/outputs/test_video.mp4"
    status_resp = Response(
        200,
        json={
            "code": 200,
            "msg": "success",
            "data": {
                "taskId": "kie-task-456",
                "state": "success",
                "resultUrl": video_cdn_url
            }
        }
    )

    # Mock Video Download Payload (valid 8+ bytes MP4 header dummy)
    dummy_mp4_bytes = b"\x00\x00\x00\x1cftypisom\x00\x00\x02\x00isomiso2avc1mp41" + b"X" * 500
    download_resp = Response(200, content=dummy_mp4_bytes)

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post, \
         patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:

        mock_post.return_value = create_resp

        def get_side_effect(url, **kwargs):
            if "recordInfo" in url:
                return status_resp
            return download_resp

        mock_get.side_effect = get_side_effect

        job_id = await provider.submit_generation(sample_generation)

        # Check status -> triggers completion and local download
        status, pct = await provider.check_status(job_id)
        assert status == GenerationStatus.COMPLETED
        assert pct == 100

        res = await provider.get_result(job_id)
        assert res["video_url"] == f"/api/v1/generations/{sample_generation.id}/video"

        # Verify local file persisted
        generated_file = os.path.join(os.getcwd(), "generated", f"moviq_{sample_generation.id}.mp4")
        assert os.path.exists(generated_file)
        assert os.path.getsize(generated_file) > 0


@pytest.mark.asyncio
async def test_kie_health_check():
    provider = KieVideoProvider(api_key="valid_key", base_url="https://api.kie.ai")
    mock_resp = Response(200, json={"code": 200, "msg": "success"})

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp
        health_info = await provider.health()
        assert health_info["status"] == "HEALTHY"
        assert health_info["reachable"] is True


def test_kie_registry_and_factory_routing():
    orig_provider = settings.VIDEO_PROVIDER
    orig_key = settings.KIE_API_KEY

    settings.VIDEO_PROVIDER = "kie"
    settings.KIE_API_KEY = "valid_kie_test_key"

    models = get_all_models()
    kling = get_model_capability("kling-3.0/video")
    assert kling.provider == "kie"
    assert kling.configured is True
    assert kling.status_label == "READY"

    provider_inst = get_video_provider("kling-3.0/video")
    assert isinstance(provider_inst, KieVideoProvider)

    settings.VIDEO_PROVIDER = orig_provider
    settings.KIE_API_KEY = orig_key


@pytest.mark.asyncio
async def test_kie_extended_polling_in_progress(sample_generation):
    orig_prov = settings.VIDEO_PROVIDER
    settings.VIDEO_PROVIDER = "kie"
    try:
        provider = KieVideoProvider(api_key="real_live_key_xyz", base_url="https://api.kie.ai")
        create_resp = Response(200, json={"code": 200, "msg": "success", "data": {"taskId": "task-long-poll"}})
        generating_resp = Response(200, json={"code": 200, "msg": "success", "data": {"taskId": "task-long-poll", "state": "generating"}})

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post, \
             patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_post.return_value = create_resp
            mock_get.return_value = generating_resp

            job_id = await provider.submit_generation(sample_generation)
            
            # Simulate multiple polling cycles while task is still rendering on Kie.ai
            for _ in range(5):
                status, pct = await provider.check_status(job_id)
                assert status == GenerationStatus.GENERATING
                assert pct >= 30
    finally:
        settings.VIDEO_PROVIDER = orig_prov


@pytest.mark.asyncio
async def test_kie_status_failure_message_propagation(sample_generation):
    orig_prov = settings.VIDEO_PROVIDER
    settings.VIDEO_PROVIDER = "kie"
    try:
        provider = KieVideoProvider(api_key="real_live_key_xyz", base_url="https://api.kie.ai")
        create_resp = Response(200, json={"code": 200, "msg": "success", "data": {"taskId": "task-fail"}})
        fail_resp = Response(200, json={"code": 200, "msg": "success", "data": {"taskId": "task-fail", "state": "fail", "failReason": "Kie AI GPU cluster capacity busy"}})

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post, \
             patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_post.return_value = create_resp
            mock_get.return_value = fail_resp

            job_id = await provider.submit_generation(sample_generation)

            with pytest.raises(KieGenerationFailedException) as exc_info:
                await provider.check_status(job_id)
            assert "Kie AI GPU cluster capacity busy" in str(exc_info.value)
    finally:
        settings.VIDEO_PROVIDER = orig_prov


@pytest.mark.asyncio
async def test_kie_transient_http_error_recovery(sample_generation):
    orig_prov = settings.VIDEO_PROVIDER
    settings.VIDEO_PROVIDER = "kie"
    try:
        provider = KieVideoProvider(api_key="real_live_key_xyz", base_url="https://api.kie.ai")
        create_resp = Response(200, json={"code": 200, "msg": "success", "data": {"taskId": "task-transient"}})
        error_resp = Response(502, json={"error": "Bad Gateway"})

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post, \
             patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_post.return_value = create_resp
            mock_get.return_value = error_resp

            job_id = await provider.submit_generation(sample_generation)
            status, pct = await provider.check_status(job_id)
            assert status == GenerationStatus.GENERATING
    finally:
        settings.VIDEO_PROVIDER = orig_prov



