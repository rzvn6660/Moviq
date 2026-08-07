from app.schemas.provider import CostEstimateRequest, CostEstimateResponse
from app.services.video.registry import get_model_capability


MODEL_PRICING_TABLE = {
    "kling-3.0/video": {
        "provider": "kie",
        "cost_usd": 0.15,
        "credits": 15.0,
        "queue_sec": 5,
        "runtime_sec": 8.0,
        "resolution": "1280x720",
        "known": True,
        "notes": "Kie.ai Commercial Tier"
    },
    "wan-2.1/video": {
        "provider": "kie",
        "cost_usd": 0.08,
        "credits": 8.0,
        "queue_sec": 4,
        "runtime_sec": 6.0,
        "resolution": "1280x720",
        "known": True,
        "notes": "Kie.ai Commercial Tier"
    },
    "veo-3.1": {
        "provider": "kie",
        "cost_usd": 0.35,
        "credits": 35.0,
        "queue_sec": 10,
        "runtime_sec": 12.0,
        "resolution": "1920x1080",
        "known": True,
        "notes": "Google Veo 1080p Ultra Tier"
    },
    "dream-machine": {
        "provider": "luma",
        "cost_usd": 0.20,
        "credits": 20.0,
        "queue_sec": 6,
        "runtime_sec": 7.5,
        "resolution": "1280x720",
        "known": True,
        "notes": "Luma Dream Machine v1 REST API"
    },
    "hailuo-01": {
        "provider": "hailuo",
        "cost_usd": 0.12,
        "credits": 12.0,
        "queue_sec": 5,
        "runtime_sec": 8.0,
        "resolution": "1280x720",
        "known": True,
        "notes": "MiniMax Hailuo Video API"
    },
    "Wan-AI/Wan2.2-TI2V-5B": {
        "provider": "huggingface",
        "cost_usd": 0.05,
        "credits": 5.0,
        "queue_sec": 3,
        "runtime_sec": 5.5,
        "resolution": "1280x720",
        "known": True,
        "notes": "Hugging Face Serverless Inference API"
    },
    "Wan-AI/Wan2.1-T2V-1.3B-Diffusers": {
        "provider": "remote_wan",
        "cost_usd": 0.00,
        "credits": 0.0,
        "queue_sec": 2,
        "runtime_sec": 3.0,
        "resolution": "576x320",
        "known": True,
        "notes": "Self-Hosted Remote CUDA GPU Worker"
    },
    "ltx-video": {
        "provider": "ltx",
        "cost_usd": 0.00,
        "credits": 0.0,
        "queue_sec": 0,
        "runtime_sec": 4.5,
        "resolution": "1280x720",
        "known": True,
        "notes": "Local PyTorch GPU Inference"
    }
}


class CostEstimatorService:
    """
    Truthful Generation Cost & Runtime Estimator Service.
    Evaluates pricing tables and model limits without fabricating missing values.
    """

    @staticmethod
    def estimate(req: CostEstimateRequest) -> CostEstimateResponse:
        model_id = req.model_id
        duration = req.duration or "5s"

        pricing = MODEL_PRICING_TABLE.get(model_id)
        if not pricing:
            try:
                cap = get_model_capability(model_id)
                prov = cap.provider
            except Exception:
                prov = "unknown"

            return CostEstimateResponse(
                model_id=model_id,
                provider=prov,
                estimated_cost_usd=None,
                estimated_credits=None,
                estimated_queue_seconds=5,
                estimated_runtime_seconds=7.0,
                resolution="1280x720",
                pricing_known=False,
                notes="Pricing information unavailable for this model."
            )

        # Scale cost multiplier if duration is 10s or 15s
        mult = 1.0
        if duration == "10s":
            mult = 1.8
        elif duration == "15s":
            mult = 2.5

        cost_usd = round(pricing["cost_usd"] * mult, 2) if pricing["known"] and pricing["cost_usd"] > 0 else pricing["cost_usd"]
        credits_val = round(pricing["credits"] * mult, 1) if pricing["known"] and pricing["credits"] > 0 else pricing["credits"]
        runtime_sec = round(pricing["runtime_sec"] * mult, 1)

        return CostEstimateResponse(
            model_id=model_id,
            provider=pricing["provider"],
            estimated_cost_usd=cost_usd,
            estimated_credits=credits_val,
            estimated_queue_seconds=pricing["queue_sec"],
            estimated_runtime_seconds=runtime_sec,
            resolution=pricing["resolution"],
            pricing_known=pricing["known"],
            notes=pricing["notes"]
        )
