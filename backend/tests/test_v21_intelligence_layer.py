import pytest
from app.services.provider_health import ProviderHealthService
from app.services.provider_recommender import ProviderRecommenderService
from app.services.cost_estimator import CostEstimatorService
from app.services.provider_benchmark import ProviderBenchmarkService
from app.schemas.provider import RecommendProviderRequest, CostEstimateRequest
from app.utils.video_validator import validate_video_file, generate_synthetic_mp4


@pytest.mark.asyncio
async def test_provider_health_service():
    res = await ProviderHealthService.get_all_provider_health(force_refresh=True)
    assert len(res.providers) == 6
    provider_names = [p.provider for p in res.providers]
    assert "kie" in provider_names
    assert "luma" in provider_names
    assert "hailuo" in provider_names
    assert "huggingface" in provider_names
    assert "remote_wan" in provider_names
    assert "ltx" in provider_names


def test_provider_health_endpoint(client):
    res = client.get("/api/v1/providers/health")
    assert res.status_code == 200
    data = res.json()
    assert "providers" in data
    assert len(data["providers"]) == 6


def test_deterministic_recommender_engine():
    # Rule 1: Anime -> Hailuo
    req_anime = RecommendProviderRequest(prompt="Anime girl fighting dragons with katana")
    res_anime = ProviderRecommenderService.recommend(req_anime)
    assert res_anime.recommended_provider == "hailuo"
    assert res_anime.confidence >= 90

    # Rule 2: Car / Drifting -> Kie Kling
    req_car = RecommendProviderRequest(prompt="Red sports car drifting in rainy neon Tokyo")
    res_car = ProviderRecommenderService.recommend(req_car)
    assert res_car.recommended_provider == "kie"
    assert res_car.confidence >= 90

    # Rule 3: Nature -> Luma
    req_nature = RecommendProviderRequest(prompt="Forest waterfall surrounded by mossy rocks")
    res_nature = ProviderRecommenderService.recommend(req_nature)
    assert res_nature.recommended_provider == "luma"
    assert res_nature.confidence >= 90

    # Rule 4: Local -> LTX
    req_local = RecommendProviderRequest(prompt="Macro shot of leaf", priority="local")
    res_local = ProviderRecommenderService.recommend(req_local)
    assert res_local.recommended_provider == "ltx"
    assert res_local.confidence >= 90


def test_recommend_endpoint(client):
    res = client.post("/api/v1/providers/recommend", json={
        "prompt": "Futuristic cyberpunk sports car",
        "aspectRatio": "16:9",
        "priority": "quality"
    })
    assert res.status_code == 200
    data = res.json()
    assert "recommended_provider" in data
    assert "confidence" in data
    assert "reason" in data


def test_cost_estimator_service():
    req_kling = CostEstimateRequest(modelId="kling-3.0/video", duration="5s")
    res_kling = CostEstimatorService.estimate(req_kling)
    assert res_kling.pricing_known is True
    assert res_kling.estimated_cost_usd == 0.15
    assert res_kling.estimated_credits == 15.0

    req_ltx = CostEstimateRequest(modelId="ltx-video", duration="5s")
    res_ltx = CostEstimatorService.estimate(req_ltx)
    assert res_ltx.pricing_known is True
    assert res_ltx.estimated_cost_usd == 0.0

    req_unknown = CostEstimateRequest(modelId="unknown-custom-model", duration="5s")
    res_unknown = CostEstimatorService.estimate(req_unknown)
    assert res_unknown.pricing_known is False
    assert res_unknown.estimated_cost_usd is None


def test_estimate_cost_endpoint(client):
    res = client.post("/api/v1/providers/estimate-cost", json={
        "modelId": "dream-machine",
        "duration": "5s"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["provider"] == "luma"
    assert data["pricing_known"] is True
    assert data["estimated_cost_usd"] == 0.20


def test_provider_benchmarks_endpoint(client):
    res = client.get("/api/v1/providers/benchmarks")
    assert res.status_code == 200
    data = res.json()
    assert "benchmarks" in data
    assert len(data["benchmarks"]) == 6


def test_video_validation_v2_synthetic_and_invalid(tmp_path):
    mp4_path = str(tmp_path / "valid_test.mp4")
    res_val = generate_synthetic_mp4(mp4_path, prompt="Testing video validation v2")
    assert res_val["valid"] is True
    assert res_val["error"] is None
    assert res_val["sha256"] is not None
