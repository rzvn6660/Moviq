import pytest
import asyncio
from unittest.mock import AsyncMock, patch
import httpx


from app.api.generations import is_safe_download_url
from app.core.config import settings
from app.models.generation import Generation
from app.schemas.common import GenerationStatus


def test_generation_timeout_config():
    assert settings.GENERATION_TIMEOUT_SECONDS == 600


def test_idempotency_duplicate_key(client):
    idempotency_key = "idemp-key-unique-test-12345"
    payload = {
        "prompt": "Cyberpunk city with flying cars in 8K",
        "style": "Cinematic",
        "aspectRatio": "16:9",
        "duration": "5s",
        "modelId": "Wan-AI/Wan2.2-TI2V-5B"
    }

    # First request
    res1 = client.post(
        "/api/v1/generations",
        json=payload,
        headers={"Idempotency-Key": idempotency_key}
    )
    assert res1.status_code == 201
    gen_id_1 = res1.json()["id"]

    # Second request with EXACT SAME key
    res2 = client.post(
        "/api/v1/generations",
        json=payload,
        headers={"Idempotency-Key": idempotency_key}
    )
    assert res2.status_code in (200, 201)
    gen_id_2 = res2.json()["id"]

    # Must return the exact same generation record
    assert gen_id_1 == gen_id_2


def test_idempotency_different_keys(client):
    payload = {
        "prompt": "Cyberpunk city with flying cars in 8K",
        "style": "Cinematic",
        "aspectRatio": "16:9",
        "duration": "5s",
        "modelId": "Wan-AI/Wan2.2-TI2V-5B"
    }

    res1 = client.post(
        "/api/v1/generations",
        json=payload,
        headers={"Idempotency-Key": "key-alpha-001"}
    )
    res2 = client.post(
        "/api/v1/generations",
        json=payload,
        headers={"Idempotency-Key": "key-beta-002"}
    )

    assert res1.json()["id"] != res2.json()["id"]


@pytest.mark.asyncio
async def test_completion_lifecycle_processing_validated(db_session):
    from app.services.generation_service import GenerationService
    from app.schemas.generation import CreateGenerationRequest

    service = GenerationService(db_session)
    req = CreateGenerationRequest(
        prompt="Perfume bottle on marble",
        style="Cinematic",
        aspectRatio="16:9",
        duration="5s",
        modelId="Wan-AI/Wan2.2-TI2V-5B"
    )

    res = await service.create_generation(request=req, idempotency_key="lifecycle-key-1")
    gen_id = res.id

    # Give event loop time to complete async mock lifecycle
    await asyncio.sleep(1.2)

    status_res = await service.get_generation_status(gen_id)
    assert status_res.state == GenerationStatus.COMPLETED
    assert status_res.video.video_url.startswith("http") or status_res.video.video_url.startswith("/api/v1")


@pytest.mark.asyncio
async def test_invalid_result_after_completion(db_session):
    from app.services.generation_service import GenerationService
    from app.schemas.generation import CreateGenerationRequest

    service = GenerationService(db_session)
    req = CreateGenerationRequest(
        prompt="Invalid result test prompt",
        style="Cinematic",
        aspectRatio="16:9",
        duration="5s",
        modelId="Wan-AI/Wan2.2-TI2V-5B"
    )

    # Mock provider returning COMPLETED status but invalid empty video URL
    mock_provider = AsyncMock()
    mock_provider.submit_generation = AsyncMock(return_value="mock-job-invalid-123")
    mock_provider.check_status = AsyncMock(return_value=(GenerationStatus.COMPLETED, 100))
    mock_provider.get_result = AsyncMock(return_value={"video_url": ""})  # Invalid URL

    service.video_provider = mock_provider

    res = await service.create_generation(request=req, idempotency_key="invalid-res-key")
    gen_id = res.id

    status_res = await service.get_generation_status(gen_id)
    assert status_res.state == GenerationStatus.FAILED


def test_download_security_rejections():
    # Should reject unsafe targets
    assert is_safe_download_url("http://localhost:8000/secret") is False
    assert is_safe_download_url("http://127.0.0.1/admin") is False
    assert is_safe_download_url("http://10.0.0.1/internal") is False
    assert is_safe_download_url("http://192.168.1.1/config") is False
    assert is_safe_download_url("ftp://example.com/file.mp4") is False
    assert is_safe_download_url("file:///etc/passwd") is False
    assert is_safe_download_url("invalid_url_string") is False

    # Should accept valid external media URLs
    assert is_safe_download_url("https://fal.media/files/video.mp4") is True
    assert is_safe_download_url("https://commondatastorage.googleapis.com/sample.mp4") is True


def test_download_streaming_security(client, db_session):
    from app.db.repositories.generations import GenerationsRepository
    repo = GenerationsRepository(db_session)

    # 1. Unsafe URL should be rejected
    gen_unsafe = Generation(
        id="gen-unsafe-url",
        original_prompt="Unsafe URL test",
        status=GenerationStatus.COMPLETED,
        video_url="http://127.0.0.1:8000/internal"
    )
    repo.create(gen_unsafe)

    res_unsafe = client.get("/api/v1/generations/gen-unsafe-url/download")
    assert res_unsafe.status_code in (400, 422)
    assert "error" in res_unsafe.json()
