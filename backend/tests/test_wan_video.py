import os
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.services.video.wan import WanVideoProvider
from app.services.video.factory import get_video_provider
from app.models.generation import Generation
from app.schemas.common import GenerationStatus
from app.core.config import settings
from app.core.exceptions import (
    WANDependenciesMissingException,
    WANCUDAUnavailableException,
    WANGenerationFailedException,
    WANInvalidOutputException,
)


@pytest.mark.asyncio
async def test_wan_video_provider_missing_dependencies():
    provider = WanVideoProvider()
    gen = Generation(id="gen-wan-missing-deps", original_prompt="test", status=GenerationStatus.QUEUED)

    with patch.dict("sys.modules", {"torch": None}):
        with pytest.raises(WANDependenciesMissingException):
            await provider.submit_generation(gen)


@pytest.mark.asyncio
async def test_wan_video_provider_cuda_unavailable():
    provider = WanVideoProvider()
    gen = Generation(id="gen-wan-no-cuda", original_prompt="test", status=GenerationStatus.QUEUED)

    mock_torch = MagicMock()
    mock_torch.cuda.is_available.return_value = False

    with patch.dict("sys.modules", {"torch": mock_torch, "diffusers": MagicMock(), "transformers": MagicMock()}):
        with pytest.raises(WANCUDAUnavailableException):
            await provider.submit_generation(gen)


@pytest.mark.asyncio
async def test_wan_video_provider_successful_generation():
    provider = WanVideoProvider()
    gen = Generation(
        id="moviq-gen-wan-test-1",
        original_prompt="A cybernetic eagle soaring above a foggy mountain peak",
        enhanced_prompt="Cinematic shot of a cybernetic eagle soaring above a foggy mountain peak...",
        negative_prompt="blurry",
        aspect_ratio="16:9",
        duration="5s"
    )

    mock_torch = MagicMock()
    mock_torch.cuda.is_available.return_value = True
    mock_torch.float16 = "float16"

    mock_diffusers = MagicMock()
    mock_pipeline_inst = MagicMock()
    mock_pipeline_inst.return_value.frames = [[b"frame1", b"frame2"]]
    mock_diffusers.WanPipeline.from_pretrained.return_value = mock_pipeline_inst

    # Mock video export writing a dummy MP4 file
    def mock_export(frames, filepath, fps):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "wb") as f:
            f.write(b"mock wan2.1 video binary content")

    mock_diffusers.utils.export_to_video = mock_export

    modules_dict = {
        "torch": mock_torch,
        "diffusers": mock_diffusers,
        "diffusers.utils": mock_diffusers.utils,
        "transformers": MagicMock()
    }

    with patch.dict("sys.modules", modules_dict):
        job_id = await provider.submit_generation(gen)
        assert job_id.startswith("wan-job-")

        import asyncio
        await asyncio.sleep(0.4)

        status, pct = await provider.check_status(job_id)
        assert status == GenerationStatus.COMPLETED

        result = await provider.get_result(job_id)
        assert result["video_url"] == "/api/v1/generations/moviq-gen-wan-test-1/video"

        # Verify local file persisted
        filepath = os.path.join(os.getcwd(), "generated", "moviq_moviq-gen-wan-test-1.mp4")
        assert os.path.exists(filepath)


def test_wan_factory_selection():
    settings.VIDEO_PROVIDER = "wan"
    p_wan = get_video_provider()
    assert "Wan" in p_wan.__class__.__name__

    settings.VIDEO_PROVIDER = "mock"
    p_mock = get_video_provider()
    assert "Mock" in p_mock.__class__.__name__

    settings.VIDEO_PROVIDER = "fal"
    p_fal = get_video_provider()
    assert "Fal" in p_fal.__class__.__name__

    settings.VIDEO_PROVIDER = "huggingface"
    p_hf = get_video_provider()
    assert "HuggingFace" in p_hf.__class__.__name__

    settings.VIDEO_PROVIDER = "mock"
