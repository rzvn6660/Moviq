import pytest
from app.services.video.luma import LumaVideoProvider
from app.services.video.hailuo import HailuoVideoProvider
from app.services.video.ltx import LTXVideoProvider
from app.models.generation import Generation
from app.schemas.common import GenerationStatus


@pytest.mark.asyncio
async def test_luma_provider_lifecycle():
    provider = LumaVideoProvider()
    health = await provider.health_check()
    assert health["provider"] == "luma"

    models = provider.supported_models()
    assert len(models) == 1
    assert models[0]["id"] == "dream-machine"

    gen = Generation(id="test-luma-1", original_prompt="A golden retriever running in sunlight", aspect_ratio="16:9", duration="5s")
    job_id = await provider.submit_generation(gen)
    assert job_id is not None

    status, pct, result = await provider.poll_generation(job_id)
    assert status == GenerationStatus.COMPLETED
    assert pct == 100
    assert result is not None
    assert "video_url" in result


@pytest.mark.asyncio
async def test_hailuo_provider_lifecycle():
    provider = HailuoVideoProvider()
    health = await provider.health_check()
    assert health["provider"] == "hailuo"

    models = provider.supported_models()
    assert len(models) == 1
    assert models[0]["id"] == "hailuo-01"

    gen = Generation(id="test-hailuo-1", original_prompt="Cyberpunk neon city drone flythrough", aspect_ratio="16:9", duration="5s")
    job_id = await provider.submit_generation(gen)
    assert job_id is not None

    status, pct, result = await provider.poll_generation(job_id)
    assert status == GenerationStatus.COMPLETED
    assert pct == 100
    assert result is not None
    assert "video_url" in result


@pytest.mark.asyncio
async def test_ltx_provider_lifecycle():
    provider = LTXVideoProvider()
    health = await provider.health_check()
    assert health["provider"] == "ltx"

    models = provider.supported_models()
    assert len(models) == 1
    assert models[0]["id"] == "ltx-video"

    gen = Generation(id="test-ltx-1", original_prompt="Macro shot of raindrops on autumn leaf", aspect_ratio="16:9", duration="5s")
    job_id = await provider.submit_generation(gen)
    assert job_id is not None

    status, pct, result = await provider.poll_generation(job_id)
    assert status == GenerationStatus.COMPLETED
    assert pct == 100
    assert result is not None
    assert "video_url" in result
