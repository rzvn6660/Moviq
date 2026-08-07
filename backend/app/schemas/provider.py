from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ProviderCreditsInfo(BaseModel):
    known: bool = False
    remaining: Optional[float] = None


class ProviderHealthResponse(BaseModel):
    provider: str
    status: str  # ONLINE, DEGRADED, OFFLINE, AUTH_FAILED, QUOTA_EXHAUSTED, GPU_BUSY, CONFIG_MISSING
    latency_ms: int
    queue_status: str  # LOW, MEDIUM, HIGH, FULL, UNKNOWN
    configured: bool
    authenticated: bool
    available_models: int
    estimated_wait: int  # in seconds
    credits: ProviderCreditsInfo
    message: Optional[str] = None


class ProviderHealthListResponse(BaseModel):
    providers: List[ProviderHealthResponse]
    cached_at: str


class RecommendProviderRequest(BaseModel):
    prompt: str
    aspect_ratio: Optional[str] = Field("16:9", alias="aspectRatio")
    duration: Optional[str] = "5s"
    priority: Optional[str] = "quality"  # quality, speed, cost, local


class RecommendProviderResponse(BaseModel):
    recommended_provider: str
    recommended_model_id: str
    confidence: int  # Percentage 0-100
    reason: str
    fallback_providers: List[str]


class CostEstimateRequest(BaseModel):
    model_id: str = Field(..., alias="modelId")
    duration: Optional[str] = "5s"
    aspect_ratio: Optional[str] = Field("16:9", alias="aspectRatio")


class CostEstimateResponse(BaseModel):
    model_id: str
    provider: str
    estimated_cost_usd: Optional[float] = None
    estimated_credits: Optional[float] = None
    estimated_queue_seconds: int = 5
    estimated_runtime_seconds: float = 5.0
    resolution: str = "1280x720"
    pricing_known: bool = False
    notes: str = "Standard tier estimation"


class ProviderBenchmarkMetric(BaseModel):
    provider: str
    name: str
    avg_generation_time_seconds: float
    avg_queue_time_seconds: float
    success_rate_percentage: float
    total_generations: int
    supported_resolutions: List[str]
    typical_duration: str
    estimated_cost_per_sec: Optional[float] = None
    motion_quality_score: float
    realism_score: float
    reliability_score: float
    overall_rating: str  # EXCELLENT, GOOD, FAIR, POOR


class ProviderBenchmarkListResponse(BaseModel):
    benchmarks: List[ProviderBenchmarkMetric]
