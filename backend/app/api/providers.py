from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.provider import (
    ProviderHealthListResponse,
    RecommendProviderRequest,
    RecommendProviderResponse,
    CostEstimateRequest,
    CostEstimateResponse,
    ProviderBenchmarkListResponse,
)
from app.services.provider_health import ProviderHealthService
from app.services.provider_recommender import ProviderRecommenderService
from app.services.cost_estimator import CostEstimatorService
from app.services.provider_benchmark import ProviderBenchmarkService

router = APIRouter(prefix="/providers", tags=["Providers"])


@router.get("/health", response_model=ProviderHealthListResponse)
async def get_provider_health(force_refresh: bool = Query(False, alias="refresh")):
    """
    Exposes real-time provider health dashboard status for all 6 supported video providers.
    Includes status (ONLINE, DEGRADED, OFFLINE, AUTH_FAILED, QUOTA_EXHAUSTED, GPU_BUSY, CONFIG_MISSING),
    latency, queue status, credentials state, and estimated wait times.
    """
    return await ProviderHealthService.get_all_provider_health(force_refresh=force_refresh)


@router.post("/recommend", response_model=RecommendProviderResponse)
async def recommend_provider(request: RecommendProviderRequest):
    """
    Deterministic rule-based AI provider recommendation engine based on prompt semantics,
    aspect ratio, duration, and priority preferences.
    """
    return ProviderRecommenderService.recommend(request)


@router.post("/estimate-cost", response_model=CostEstimateResponse)
async def estimate_generation_cost(request: CostEstimateRequest):
    """
    Truthful generation cost & runtime estimator for a given model, duration, and aspect ratio.
    """
    return CostEstimatorService.estimate(request)


@router.get("/benchmarks", response_model=ProviderBenchmarkListResponse)
async def get_provider_benchmarks(db: Session = Depends(get_db)):
    """
    Evidence-based provider performance benchmarks aggregating empirical DB execution metrics.
    """
    return ProviderBenchmarkService.get_benchmarks(db)
