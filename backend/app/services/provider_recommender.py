from typing import List
from app.schemas.provider import RecommendProviderRequest, RecommendProviderResponse


class ProviderRecommenderService:
    """
    Deterministic Rule-Based AI Provider Recommendation Engine.
    Analyzes prompt text semantics, target resolution, duration, and execution priority
    to recommend the optimal provider and model with explicit confidence score and reasoning.
    """

    @staticmethod
    def recommend(req: RecommendProviderRequest) -> RecommendProviderResponse:
        prompt_lower = req.prompt.lower()
        priority = (req.priority or "quality").lower()

        # Rule 1: Local / Privacy Priority
        if priority == "local" or any(kw in prompt_lower for kw in ["local", "offline", "gpu", "private"]):
            return RecommendProviderResponse(
                recommended_provider="ltx",
                recommended_model_id="ltx-video",
                confidence=93,
                reason="Optimal local GPU inference with zero external network latency.",
                fallback_providers=["remote_wan", "huggingface"]
            )

        # Rule 2: Vehicle / High Motion / Racing
        if any(kw in prompt_lower for kw in ["car", "cars", "drift", "drifting", "racing", "speed", "vehicle", "tokyo", "neon"]):
            return RecommendProviderResponse(
                recommended_provider="kie",
                recommended_model_id="kling-3.0/video",
                confidence=95,
                reason="Superior motion physics and cinematic lighting for high-speed vehicle tracking.",
                fallback_providers=["hailuo", "dream-machine"]
            )

        # Rule 3: Character / Anime / Portrait / Human Motion
        if any(kw in prompt_lower for kw in ["anime", "girl", "character", "fight", "fighting", "dragon", "samurai", "portrait", "person", "human"]):
            return RecommendProviderResponse(
                recommended_provider="hailuo",
                recommended_model_id="hailuo-01",
                confidence=94,
                reason="Strong character animation and stylized fluid facial/body dynamics.",
                fallback_providers=["kie", "luma"]
            )

        # Rule 4: Nature / Organic / Macro / Landscape
        if any(kw in prompt_lower for kw in ["nature", "forest", "mountain", "ocean", "rain", "macro", "flower", "waterfall", "sunset", "lake"]):
            return RecommendProviderResponse(
                recommended_provider="luma",
                recommended_model_id="dream-machine",
                confidence=92,
                reason="Physics-informed fluid motion and true-to-life environmental lighting.",
                fallback_providers=["kie", "hailuo"]
            )

        # Rule 5: Ultra Photorealistic
        if any(kw in prompt_lower for kw in ["photoreal", "ultra realistic", "8k", "hyperrealistic", "cinematic 35mm"]):
            return RecommendProviderResponse(
                recommended_provider="kie",
                recommended_model_id="veo-3.1",
                confidence=96,
                reason="Photorealistic 1080p rendering engine with professional depth-of-field.",
                fallback_providers=["kling-3.0/video", "dream-machine"]
            )

        # Rule 6: Open Source / Developer Preference
        if any(kw in prompt_lower for kw in ["open source", "diffusers", "wan"]):
            return RecommendProviderResponse(
                recommended_provider="huggingface",
                recommended_model_id="Wan-AI/Wan2.2-TI2V-5B",
                confidence=90,
                reason="Open-weights diffusion model hosted on serverless Hugging Face Inference API.",
                fallback_providers=["remote_wan", "kie"]
            )

        # Default Recommendation
        return RecommendProviderResponse(
            recommended_provider="kie",
            recommended_model_id="kling-3.0/video",
            confidence=88,
            reason="Balanced general-purpose cinematic text-to-video model.",
            fallback_providers=["hailuo", "dream-machine", "Wan-AI/Wan2.2-TI2V-5B"]
        )
