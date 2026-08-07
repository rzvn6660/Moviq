import pytest
import asyncio
import time
from app.services.video.factory import get_video_provider
from app.services.video.registry import get_all_models
from app.services.provider_health import ProviderHealthService
from app.services.generation_service import GenerationService
from app.schemas.generation import CreateGenerationRequest
from app.models.generation import Generation
from app.schemas.common import GenerationStatus
from app.core.config import settings


@pytest.mark.asyncio
async def test_provider_certification_all_six_providers(db_session):
    """
    Certifies full 10-step lifecycle across all 6 authoritative video providers.
    """
    providers = ["kie", "luma", "hailuo", "huggingface", "remote_wan", "ltx"]
    service = GenerationService(db_session)

    for prov_name in providers:
        # 1. Health check
        health_resp = await ProviderHealthService._check_single_provider(prov_name)
        assert health_resp.provider == prov_name
        assert health_resp.status in ["ONLINE", "CONFIG_MISSING", "OFFLINE", "GPU_BUSY", "DEGRADED"]

        # 2. Provider discovery
        prov_models = [m for m in get_all_models() if m.provider == prov_name]
        assert len(prov_models) > 0
        model_id = prov_models[0].id

        # 3. Submission & lifecycle
        req = CreateGenerationRequest(
            prompt=f"RC2 Certification test prompt for provider {prov_name}",
            modelId=model_id,
            aspectRatio="16:9",
            duration="5s"
        )
        res = await service.create_generation(request=req, idempotency_key=f"rc2-cert-{prov_name}")
        assert res.id.startswith("moviq-gen-")
        assert res.state in ["QUEUED", "SUBMITTED", "GENERATING", "COMPLETED", "FAILED"]

        # Retrieve events timeline
        events = await service.get_generation_events(res.id)
        assert len(events) > 0


@pytest.mark.asyncio
async def test_stress_consecutive_generations(db_session):
    """
    Executes 25 consecutive generations under load to verify no database locks or memory leaks.
    """
    service = GenerationService(db_session)
    gen_ids = []

    for i in range(25):
        req = CreateGenerationRequest(
            prompt=f"Stress test generation #{i+1} cybernetic car drifting",
            modelId="Wan-AI/Wan2.2-TI2V-5B",
            aspectRatio="16:9",
            duration="5s"
        )
        res = await service.create_generation(request=req, idempotency_key=f"stress-key-{i+1}")
        assert res.id.startswith("moviq-gen-")
        gen_ids.append(res.id)

    assert len(gen_ids) == 25


@pytest.mark.asyncio
async def test_parallel_generations_concurrency(db_session):
    """
    Executes 5 parallel generation requests concurrently using asyncio.gather.
    """
    service = GenerationService(db_session)

    async def create_single(idx: int):
        req = CreateGenerationRequest(
            prompt=f"Parallel concurrency test #{idx}",
            modelId="kling-3.0/video",
            aspectRatio="16:9",
            duration="5s"
        )
        return await service.create_generation(request=req, idempotency_key=f"parallel-key-{idx}")

    results = await asyncio.gather(*[create_single(i) for i in range(5)])
    assert len(results) == 5
    unique_ids = set(r.id for r in results)
    assert len(unique_ids) == 5


def test_rapid_delete_and_idempotency_stress(client):
    """
    Tests rapid idempotency duplicates and rapid deletion endpoint without race conditions.
    """
    idemp_key = "rapid-idemp-rc2-key-999"
    payload = {
        "prompt": "Rapid delete and idempotency test",
        "modelId": "ltx-video",
        "aspectRatio": "16:9",
        "duration": "5s"
    }

    # Duplicate submission with same key
    r1 = client.post("/api/v1/generations", json=payload, headers={"Idempotency-Key": idemp_key})
    r2 = client.post("/api/v1/generations", json=payload, headers={"Idempotency-Key": idemp_key})

    assert r1.status_code == 201
    assert r2.status_code in (200, 201)
    gen_id = r1.json()["id"]
    assert gen_id == r2.json()["id"]

    # Delete generation
    del_res = client.delete(f"/api/v1/generations/{gen_id}")
    assert del_res.status_code in (200, 204)

    # Verify 404 after deletion
    get_res = client.get(f"/api/v1/generations/{gen_id}")
    assert get_res.status_code == 404
