import pytest
from unittest.mock import AsyncMock, patch
import httpx

from app.services.video.fal import FalVideoProvider
from app.services.video.factory import get_video_provider
from app.models.generation import Generation
from app.schemas.common import GenerationStatus
from app.core.exceptions import (
    FalConfigurationErrorException,
    FalAuthenticationErrorException,
    FalRateLimitedException,
    FalProviderUnavailableException,
    FalResultErrorException,
)


@pytest.mark.asyncio
async def test_fal_video_provider_submission_success():
    provider = FalVideoProvider(api_key="fal_mock_key_12345", model="fal-ai/kling-video/v2.5-turbo/pro/text-to-video")

    gen = Generation(
        id="moviq-gen-test1",
        original_prompt="A cybernetic panther prowling on neon street",
        enhanced_prompt="Cinematic macro shot of cybernetic panther prowling on rainy neon street...",
        negative_prompt="blurry, low quality",
        aspect_ratio="16:9",
        duration="5s"
    )

    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json = lambda: {"request_id": "fal-req-abcdef123"}

    with patch.object(httpx.AsyncClient, "post", return_value=mock_response) as mock_post:
        req_id = await provider.submit_generation(gen)
        assert req_id == "fal-req-abcdef123"

        # Verify request parameters
        called_kwargs = mock_post.call_args.kwargs
        json_body = called_kwargs["json"]
        assert json_body["prompt"] == gen.enhanced_prompt
        assert json_body["duration"] == "5"
        assert json_body["aspect_ratio"] == "16:9"
        assert json_body["negative_prompt"] == "blurry, low quality"
        assert json_body["cfg_scale"] == 0.5


@pytest.mark.asyncio
async def test_fal_video_provider_status_lifecycle():
    provider = FalVideoProvider(api_key="fal_mock_key", model="fal-ai/kling-video/v2.5-turbo/pro/text-to-video")

    # 1. IN_QUEUE -> SUBMITTED
    resp_queue = AsyncMock()
    resp_queue.status_code = 200
    resp_queue.json = lambda: {"status": "IN_QUEUE"}

    with patch.object(httpx.AsyncClient, "get", return_value=resp_queue):
        status, pct = await provider.check_status("req-123")
        assert status == GenerationStatus.SUBMITTED

    # 2. IN_PROGRESS -> GENERATING
    resp_prog = AsyncMock()
    resp_prog.status_code = 200
    resp_prog.json = lambda: {"status": "IN_PROGRESS"}

    with patch.object(httpx.AsyncClient, "get", return_value=resp_prog):
        status, pct = await provider.check_status("req-123")
        assert status == GenerationStatus.GENERATING

    # 3. COMPLETED -> COMPLETED
    resp_comp = AsyncMock()
    resp_comp.status_code = 200
    resp_comp.json = lambda: {"status": "COMPLETED"}

    with patch.object(httpx.AsyncClient, "get", return_value=resp_comp):
        status, pct = await provider.check_status("req-123")
        assert status == GenerationStatus.COMPLETED


@pytest.mark.asyncio
async def test_fal_video_provider_result_extraction():
    provider = FalVideoProvider(api_key="fal_mock_key", model="fal-ai/kling-video/v2.5-turbo/pro/text-to-video")

    mock_resp = AsyncMock()
    mock_resp.status_code = 200
    mock_resp.json = lambda: {
        "video": {"url": "https://fal.media/files/kling_video_output.mp4"},
        "thumbnail": {"url": "https://fal.media/files/kling_thumb.jpg"},
        "timings": {"inference": 8.2}
    }

    with patch.object(httpx.AsyncClient, "get", return_value=mock_resp):
        res = await provider.get_result("req-123")
        assert res["video_url"] == "https://fal.media/files/kling_video_output.mp4"
        assert res["thumbnail_url"] == "https://fal.media/files/kling_thumb.jpg"
        assert res["generation_time_seconds"] == 8.2


@pytest.mark.asyncio
async def test_fal_video_provider_malformed_result():
    provider = FalVideoProvider(api_key="fal_mock_key")
    mock_resp = AsyncMock()
    mock_resp.status_code = 200
    mock_resp.json = lambda: {"video": {}}  # Missing URL

    with patch.object(httpx.AsyncClient, "get", return_value=mock_resp):
        with pytest.raises(FalResultErrorException):
            await provider.get_result("req-123")


@pytest.mark.asyncio
async def test_fal_video_provider_missing_key():
    provider = FalVideoProvider(api_key="")
    gen = Generation(id="gen-test", original_prompt="test", status=GenerationStatus.QUEUED)
    with pytest.raises(FalConfigurationErrorException):
        await provider.submit_generation(gen)


@pytest.mark.asyncio
async def test_fal_video_provider_auth_error():
    provider = FalVideoProvider(api_key="invalid_key")
    mock_resp = AsyncMock()
    mock_resp.status_code = 401

    gen = Generation(id="gen-test", original_prompt="test", status=GenerationStatus.QUEUED)
    with patch.object(httpx.AsyncClient, "post", return_value=mock_resp):
        with pytest.raises(FalAuthenticationErrorException):
            await provider.submit_generation(gen)


@pytest.mark.asyncio
async def test_fal_video_provider_rate_limited():
    provider = FalVideoProvider(api_key="fal_key")
    mock_resp = AsyncMock()
    mock_resp.status_code = 429

    gen = Generation(id="gen-test", original_prompt="test", status=GenerationStatus.QUEUED)
    with patch.object(httpx.AsyncClient, "post", return_value=mock_resp):
        with pytest.raises(FalRateLimitedException):
            await provider.submit_generation(gen)


def test_video_factory_selection():
    from app.core.config import settings
    settings.VIDEO_PROVIDER = "mock"
    p_mock = get_video_provider()
    assert "Mock" in p_mock.__class__.__name__

    settings.VIDEO_PROVIDER = "fal"
    p_fal = get_video_provider()
    assert "Fal" in p_fal.__class__.__name__ or "HuggingFace" in p_fal.__class__.__name__

    settings.VIDEO_PROVIDER = "mock"


def test_download_endpoint(client, db_session):
    from app.models.generation import Generation
    from app.schemas.common import GenerationStatus

    gen = Generation(
        id="moviq-gen-dl-test-100",
        original_prompt="Download test prompt",
        enhanced_prompt="Download test enhanced prompt",
        status=GenerationStatus.COMPLETED,
        video_url="https://fal.media/files/sample_output.mp4"
    )
    db_session.add(gen)
    db_session.commit()

    res_dl = client.get("/api/v1/generations/moviq-gen-dl-test-100/download")
    assert res_dl.status_code in (200, 302)
