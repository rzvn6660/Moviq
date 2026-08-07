import os
import time
import asyncio
import httpx
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from app.schemas.provider import ProviderHealthResponse, ProviderCreditsInfo, ProviderHealthListResponse
from app.services.video.factory import get_video_provider
from app.services.video.registry import get_all_models
from app.core.config import settings
from app.core.logging import logger

_HEALTH_CACHE: Dict[str, Any] = {}
_CACHE_LOCK = asyncio.Lock()
CACHE_TTL_SECONDS = getattr(settings, "HEALTH_CACHE_TTL_SECONDS", 45.0)


class ProviderHealthService:
    """
    Production Provider Health Monitoring Service.
    Performs real-time health checks, latency measurements, and credential evaluation
    with a 45-second async cache lock to optimize throughput.
    """

    @staticmethod
    async def get_all_provider_health(force_refresh: bool = False) -> ProviderHealthListResponse:
        now = time.time()
        async with _CACHE_LOCK:
            if not force_refresh and "data" in _HEALTH_CACHE and (now - _HEALTH_CACHE.get("timestamp", 0)) < CACHE_TTL_SECONDS:
                return _HEALTH_CACHE["data"]

            providers = ["kie", "luma", "hailuo", "huggingface", "remote_wan", "ltx"]
            tasks = [ProviderHealthService._check_single_provider(p) for p in providers]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            health_responses: List[ProviderHealthResponse] = []
            for p_name, res in zip(providers, results):
                if isinstance(res, Exception):
                    logger.warning(f"Health check failed for provider '{p_name}': {res}")
                    health_responses.append(
                        ProviderHealthResponse(
                            provider=p_name,
                            status="OFFLINE",
                            latency_ms=0,
                            queue_status="UNKNOWN",
                            configured=False,
                            authenticated=False,
                            available_models=0,
                            estimated_wait=0,
                            credits=ProviderCreditsInfo(known=False, remaining=None),
                            message=str(res)
                        )
                    )
                else:
                    health_responses.append(res)

            cached_at = datetime.now(timezone.utc).isoformat()
            response = ProviderHealthListResponse(providers=health_responses, cached_at=cached_at)
            _HEALTH_CACHE["data"] = response
            _HEALTH_CACHE["timestamp"] = now
            return response

    @staticmethod
    async def _check_single_provider(provider_name: str) -> ProviderHealthResponse:
        start = time.time()
        is_mock_mode = settings.VIDEO_PROVIDER.lower() == "mock"

        # Count available models for this provider
        all_models = get_all_models()
        provider_models = [m for m in all_models if m.provider == provider_name]
        avail_count = len([m for m in provider_models if m.is_available])

        try:
            prov_instance = get_video_provider(provider_name)
            raw_health = await prov_instance.health_check()
            latency = int((time.time() - start) * 1000)

            status_str = raw_health.get("status", "ONLINE")
            if is_mock_mode:
                return ProviderHealthResponse(
                    provider=provider_name,
                    status="ONLINE",
                    latency_ms=max(12, latency),
                    queue_status="LOW",
                    configured=True,
                    authenticated=True,
                    available_models=len(provider_models) or 1,
                    estimated_wait=5,
                    credits=ProviderCreditsInfo(known=False, remaining=None),
                    message="Operating in local development mock mode"
                )

            # Evaluate real production status codes based on configuration and response
            status = "ONLINE"
            configured = True
            authenticated = True

            if status_str in ("NOT AVAILABLE", "CONFIG_MISSING", "OFFLINE"):
                if status_str == "NOT AVAILABLE":
                    status = "CONFIG_MISSING"
                    configured = False
                    authenticated = False
                else:
                    status = status_str

            # Specific provider credential checks
            if provider_name == "kie":
                if not settings.KIE_API_KEY or settings.KIE_API_KEY == "your_kie_api_key_here":
                    status = "CONFIG_MISSING"
                    configured = False
                    authenticated = False

            elif provider_name == "huggingface":
                if not settings.HF_TOKEN or settings.HF_TOKEN == "your_huggingface_token_here":
                    status = "CONFIG_MISSING"
                    configured = False
                    authenticated = False

            elif provider_name == "luma":
                luma_key = os.getenv("LUMA_API_KEY")
                if not luma_key:
                    status = "CONFIG_MISSING"
                    configured = False
                    authenticated = False

            elif provider_name == "hailuo":
                hailuo_key = os.getenv("HAILUO_API_KEY") or os.getenv("MINIMAX_API_KEY")
                if not hailuo_key:
                    status = "CONFIG_MISSING"
                    configured = False
                    authenticated = False

            elif provider_name == "ltx":
                gpu_avail = raw_health.get("gpu_available", False)
                if not gpu_avail and not settings.ENABLE_SYNTHETIC_FALLBACK:
                    status = "OFFLINE"

            return ProviderHealthResponse(
                provider=provider_name,
                status=status,
                latency_ms=latency,
                queue_status="LOW" if status == "ONLINE" else "UNKNOWN",
                configured=configured,
                authenticated=authenticated,
                available_models=avail_count,
                estimated_wait=10 if status == "ONLINE" else 0,
                credits=ProviderCreditsInfo(known=False, remaining=None),
                message=raw_health.get("message")
            )

        except Exception as err:
            latency = int((time.time() - start) * 1000)
            return ProviderHealthResponse(
                provider=provider_name,
                status="OFFLINE",
                latency_ms=latency,
                queue_status="UNKNOWN",
                configured=False,
                authenticated=False,
                available_models=0,
                estimated_wait=0,
                credits=ProviderCreditsInfo(known=False, remaining=None),
                message=f"Health ping exception: {err}"
            )
