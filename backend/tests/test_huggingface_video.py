import os
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from huggingface_hub.utils import HfHubHTTPError

from app.services.video.huggingface import HuggingFaceVideoProvider
from app.services.video.factory import get_video_provider
from app.models.generation import Generation
from app.schemas.common import GenerationStatus
from app.core.config import settings
from app.core.exceptions import (
    HFConfigurationErrorException,
    HFAuthenticationErrorException,
    HFRateLimitedException,
    HFInsufficientCreditsException,
    HFModelUnavailableException,
    HFGenerationFailedException,
    HFInvalidResultException,
)


@pytest.mark.asyncio
async def test_hf_video_provider_missing_token():
    provider = HuggingFaceVideoProvider(token="")
    gen = Generation(id="gen-test-missing-token", original_prompt="test", status=GenerationStatus.QUEUED)
    with pytest.raises(HFConfigurationErrorException):
        await provider.submit_generation(gen)


@pytest.mark.asyncio
async def test_hf_video_provider_submission_and_storage(tmp_path):
    provider = HuggingFaceVideoProvider(token="hf_mock_token_12345", model="Lightricks/LTX-Video")

    gen = Generation(
        id="moviq-gen-hf-test-1",
        original_prompt="Futuristic sports car on neon street",
        enhanced_prompt="Futuristic sports car on neon street, 8K hyper-detailed",
        negative_prompt="blurry",
        aspect_ratio="16:9",
        duration="5s"
    )

    mock_bytes = b"\x00\x00\x00\x18ftypisom\x00\x00\x02\x00isomiso2avc1mp41"

    with patch("app.services.video.huggingface.InferenceClient") as mock_client_cls:
        mock_instance = MagicMock()
        mock_instance.text_to_video.return_value = mock_bytes
        mock_client_cls.return_value = mock_instance

        job_id = await provider.submit_generation(gen)
        assert job_id.startswith("hf-job-")

        # Allow background task to complete execution
        import asyncio
        await asyncio.sleep(0.3)

        status, pct = await provider.check_status(job_id)
        assert status == GenerationStatus.COMPLETED

        result = await provider.get_result(job_id)
        assert result["video_url"] == "/api/v1/generations/moviq-gen-hf-test-1/video"

        # Verify local file exists
        filepath = os.path.join(os.getcwd(), "generated", "moviq_moviq-gen-hf-test-1.mp4")
        assert os.path.exists(filepath)


@pytest.mark.asyncio
async def test_hf_video_provider_auth_error():
    provider = HuggingFaceVideoProvider(token="invalid_hf_token")
    gen = Generation(id="gen-auth-err", original_prompt="test", status=GenerationStatus.QUEUED)

    mock_resp = MagicMock()
    mock_resp.status_code = 401
    mock_resp.text = "Unauthorized token"
    err = HfHubHTTPError("Invalid token", response=mock_resp)

    with patch("app.services.video.huggingface.InferenceClient") as mock_client_cls:
        mock_instance = MagicMock()
        mock_instance.text_to_video.side_effect = err
        mock_client_cls.return_value = mock_instance

        job_id = await provider.submit_generation(gen)

        import asyncio
        await asyncio.sleep(0.3)

        with pytest.raises(HFAuthenticationErrorException):
            await provider.check_status(job_id)


@pytest.mark.asyncio
async def test_hf_video_provider_insufficient_credits():
    provider = HuggingFaceVideoProvider(token="valid_token")
    gen = Generation(id="gen-credits-err", original_prompt="test", status=GenerationStatus.QUEUED)

    mock_resp = MagicMock()
    mock_resp.status_code = 403
    mock_resp.text = "You need an active subscription or credits for this endpoint"
    err = HfHubHTTPError("Payment required", response=mock_resp)

    with patch("app.services.video.huggingface.InferenceClient") as mock_client_cls:
        mock_instance = MagicMock()
        mock_instance.text_to_video.side_effect = err
        mock_client_cls.return_value = mock_instance

        job_id = await provider.submit_generation(gen)

        import asyncio
        await asyncio.sleep(0.3)

        with pytest.raises(HFInsufficientCreditsException):
            await provider.check_status(job_id)


@pytest.mark.asyncio
async def test_hf_video_provider_model_unavailable():
    provider = HuggingFaceVideoProvider(token="valid_token")
    gen = Generation(id="gen-model-unavail", original_prompt="test", status=GenerationStatus.QUEUED)

    mock_resp = MagicMock()
    mock_resp.status_code = 503
    mock_resp.text = "Model loading or unavailable"
    err = HfHubHTTPError("Model unavailable", response=mock_resp)

    with patch("app.services.video.huggingface.InferenceClient") as mock_client_cls:
        mock_instance = MagicMock()
        mock_instance.text_to_video.side_effect = err
        mock_client_cls.return_value = mock_instance

        job_id = await provider.submit_generation(gen)

        import asyncio
        await asyncio.sleep(0.3)

        with pytest.raises(HFModelUnavailableException):
            await provider.check_status(job_id)


def test_hf_factory_selection():
    settings.VIDEO_PROVIDER = "huggingface"
    p_hf = get_video_provider()
    assert "HuggingFace" in p_hf.__class__.__name__

    settings.VIDEO_PROVIDER = "mock"
    p_mock = get_video_provider()
    assert "Mock" in p_mock.__class__.__name__

    settings.VIDEO_PROVIDER = "fal"
    p_fal = get_video_provider()
    assert "Fal" in p_fal.__class__.__name__

    settings.VIDEO_PROVIDER = "mock"


def test_local_video_serving_and_path_traversal(client, db_session):
    from app.db.repositories.generations import GenerationsRepository
    repo = GenerationsRepository(db_session)

    # Create dummy local file
    generated_dir = os.path.join(os.getcwd(), "generated")
    os.makedirs(generated_dir, exist_ok=True)
    test_filepath = os.path.join(generated_dir, "moviq_gen-local-media-100.mp4")
    with open(test_filepath, "wb") as f:
        f.write(b"mock local mp4 binary content")

    gen = Generation(
        id="gen-local-media-100",
        original_prompt="Local video test",
        status=GenerationStatus.COMPLETED,
        video_url="/api/v1/generations/gen-local-media-100/video"
    )
    repo.create(gen)

    # 1. Valid local video serving
    res_video = client.get("/api/v1/generations/gen-local-media-100/video")
    assert res_video.status_code == 200
    assert res_video.headers["content-type"] == "video/mp4"

    # 2. Local download
    res_dl = client.get("/api/v1/generations/gen-local-media-100/download")
    assert res_dl.status_code == 200
    assert "attachment" in res_dl.headers.get("content-disposition", "").lower()

    # 3. Path traversal attack attempt
    res_traversal = client.get("/api/v1/generations/..%2F..%2Fetc%2Fpasswd/video")
    assert res_traversal.status_code in (404, 422, 400)
