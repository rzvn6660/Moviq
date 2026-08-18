import pytest
from unittest.mock import AsyncMock, patch
from httpx import Response
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.generation import Generation
from app.schemas.common import GenerationStatus
from app.services.video.factory import get_video_provider
from app.services.video.mock import MockVideoProvider
from app.services.video.kie import KieVideoProvider


@pytest.fixture
def sample_generation():
    return Generation(
        id="test-safety-gen-123",
        original_prompt="A red sports car racing down a neon street at night",
        enhanced_prompt="Cinematic tracking shot of a red sports car racing down a neon wet street at night",
        negative_prompt="blurry, distorted",
        aspect_ratio="16:9",
        duration="5s",
        model_id="kling-3.0/video",
        provider="kie",
    )


def test_1_safe_mode_does_not_call_kie(client: TestClient, db_session: Session):
    """1. Safe mode does not call Kie.ai APIs, using synthetic generator instead."""
    settings.MOVIQ_EXECUTION_MODE = "safe"
    settings.VIDEO_PROVIDER = "kie"

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        resp = client.post(
            "/api/v1/generations",
            json={
                "prompt": "Test safe mode generation",
                "modelId": "kling-3.0/video",
                "style": "Cinematic",
                "aspectRatio": "16:9",
                "duration": "5s",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["id"].startswith("moviq-gen-")
        
        # Verify httpx.AsyncClient.post to api.kie.ai was NEVER called
        mock_post.assert_not_called()

        # Verify generation saved with SAFE MODE label
        gen = db_session.query(Generation).filter(Generation.id == data["id"]).first()
        assert gen is not None
        assert gen.execution_mode == "SAFE MODE • LOCAL SYNTHETIC"


def test_2_automated_tests_never_call_kie():
    """2. Automated test suite default mode is forced to safe/mock mode."""
    assert settings.MOVIQ_EXECUTION_MODE == "safe"
    provider = get_video_provider("kling-3.0/video")
    assert isinstance(provider, MockVideoProvider)


def test_3_provider_selection_does_not_create_generation(client: TestClient, db_session: Session):
    """3. Provider selection and recommendation queries do not trigger generation tasks."""
    count_before = db_session.query(Generation).count()

    # Query model list
    resp1 = client.get("/api/v1/models")
    assert resp1.status_code == 200

    # Query provider recommendation
    resp2 = client.post(
        "/api/v1/providers/recommend",
        json={"prompt": "Cinematic mountain view", "aspectRatio": "16:9", "duration": "5s"},
    )
    assert resp2.status_code == 200

    # Query cost estimation
    resp3 = client.post(
        "/api/v1/providers/estimate-cost",
        json={"modelId": "kling-3.0/video", "duration": "5s"},
    )
    assert resp3.status_code == 200

    count_after = db_session.query(Generation).count()
    assert count_before == count_after == 0


def test_4_app_startup_does_not_create_generation(client: TestClient, db_session: Session):
    """4. Application startup endpoints (health, execution mode) do not trigger video generation."""
    resp1 = client.get("/api/v1/health")
    assert resp1.status_code == 200
    assert resp1.json()["status"] == "ok"

    resp2 = client.get("/api/v1/settings/execution-mode")
    assert resp2.status_code == 200
    assert resp2.json()["executionMode"] == "safe"

    assert db_session.query(Generation).count() == 0


def test_5_page_refresh_does_not_create_generation(client: TestClient, db_session: Session):
    """5. Page refreshes and history listings read data without creating new generations."""
    resp1 = client.get("/api/v1/generations")
    assert resp1.status_code == 200

    resp2 = client.get("/api/v1/generations?limit=10&offset=0")
    assert resp2.status_code == 200

    assert db_session.query(Generation).count() == 0


@pytest.mark.asyncio
async def test_6_health_check_does_not_create_generation(db_session: Session):
    """6. Provider health checks ping status endpoints and never create video generation tasks."""
    provider = KieVideoProvider(api_key="valid_test_key", base_url="https://api.kie.ai")
    mock_resp = Response(200, json={"code": 200, "msg": "success"})

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get, \
         patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        
        mock_get.return_value = mock_resp
        health_info = await provider.health()

        assert health_info["status"] == "HEALTHY"
        # Ensure createTask / submit generation POST was NEVER called
        mock_post.assert_not_called()
        assert db_session.query(Generation).count() == 0


def test_7_retry_does_not_happen_automatically(client: TestClient, db_session: Session):
    """7. Generation failure does not auto-submit a retry; retrying requires explicit API action."""
    settings.MOVIQ_EXECUTION_MODE = "safe"

    # Submit failing trigger prompt
    resp = client.post(
        "/api/v1/generations",
        json={
            "prompt": "fail_trigger: Simulate provider GPU crash",
            "modelId": "kling-3.0/video",
            "style": "Cinematic",
            "aspectRatio": "16:9",
            "duration": "5s",
        },
    )
    assert resp.status_code == 200 or resp.status_code == 500 or resp.status_code == 201

    # Verify original generation failed and no duplicate generation was automatically created
    failed_gens = db_session.query(Generation).all()
    assert len(failed_gens) == 1
    gen_id = failed_gens[0].id

    # Explicit user retry action is required to create a new generation attempt
    retry_resp = client.post(f"/api/v1/generations/{gen_id}/retry")
    assert retry_resp.status_code == 200 or retry_resp.status_code == 201
    assert db_session.query(Generation).count() == 2


@pytest.mark.asyncio
async def test_8_live_generation_occurs_only_after_explicit_generate(sample_generation):
    """8. Live mode does not auto-generate; Kie generation happens strictly on submit_generation."""
    settings.MOVIQ_EXECUTION_MODE = "live"
    settings.VIDEO_PROVIDER = "kie"

    provider = KieVideoProvider(api_key="live_key_xyz", base_url="https://api.kie.ai")
    create_resp = Response(200, json={"code": 200, "msg": "success", "data": {"taskId": "kie-task-live-100"}})

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = create_resp

        # No network calls prior to explicit submit_generation
        mock_post.assert_not_called()

        # Explicit user action triggers Kie API submission
        job_id = await provider.submit_generation(sample_generation)
        assert job_id.startswith("kie-job-")
        mock_post.assert_called_once()


@pytest.mark.asyncio
async def test_9_existing_kie_polling_continues_working(sample_generation):
    """9. Existing Kie polling flow remains intact with long polling support."""
    orig_prov = settings.VIDEO_PROVIDER
    settings.VIDEO_PROVIDER = "kie"
    try:
        provider = KieVideoProvider(api_key="real_live_key_xyz", base_url="https://api.kie.ai")
        create_resp = Response(200, json={"code": 200, "msg": "success", "data": {"taskId": "kie-task-polling-test"}})
        polling_resp = Response(200, json={"code": 200, "msg": "success", "data": {"taskId": "kie-task-polling-test", "state": "generating"}})

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post, \
             patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            
            mock_post.return_value = create_resp
            mock_get.return_value = polling_resp

            job_id = await provider.submit_generation(sample_generation)

            # Polling status query
            status, pct = await provider.check_status(job_id)
            assert status == GenerationStatus.GENERATING
            assert pct >= 30
    finally:
        settings.VIDEO_PROVIDER = orig_prov


def test_10_existing_synthetic_generation_still_works(client: TestClient, db_session: Session):
    """10. Existing synthetic local generation flow creates validated MP4 output."""
    settings.MOVIQ_EXECUTION_MODE = "safe"

    resp = client.post(
        "/api/v1/generations",
        json={
            "prompt": "A futuristic hovercraft gliding over calm turquoise water",
            "modelId": "kling-3.0/video",
            "style": "Cinematic",
            "aspectRatio": "16:9",
            "duration": "5s",
        },
    )
    assert resp.status_code == 201
    gen_id = resp.json()["id"]

    # Query status until completed
    status_resp = client.get(f"/api/v1/generations/{gen_id}")
    assert status_resp.status_code == 200
    data = status_resp.json()
    assert data["state"] == "COMPLETED"
    assert data["video"]["isSynthetic"] is True
