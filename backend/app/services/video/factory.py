from typing import Optional
from app.services.video.base import VideoProvider
from app.services.video.registry import get_model_capability
from app.core.config import settings
from app.core.exceptions import ProviderFailureException, HFConfigurationErrorException


def get_video_provider(model_id: Optional[str] = None) -> VideoProvider:
    """
    Dynamic Multi-Model / Multi-Provider Factory.
    Routes generation to the exact provider implementation required by model_id,
    or MockVideoProvider when VIDEO_PROVIDER='mock'.
    """
    # 1. Global mock override for development/testing
    if settings.VIDEO_PROVIDER.lower() == "mock":
        from app.services.video.mock import MockVideoProvider
        return MockVideoProvider()

    # 2. Legacy global provider override if model_id is not specified
    if not model_id:
        prov = settings.VIDEO_PROVIDER.lower()
        if prov == "fal":
            from app.services.video.fal import FalVideoProvider
            return FalVideoProvider()
        elif prov == "huggingface":
            from app.services.video.huggingface import HuggingFaceVideoProvider
            return HuggingFaceVideoProvider()
        elif prov == "wan":
            from app.services.video.wan import WanVideoProvider
            return WanVideoProvider()
        elif prov == "remote_wan":
            from app.services.video.remote_wan import RemoteWanVideoProvider
            return RemoteWanVideoProvider()
        else:
            from app.services.video.mock import MockVideoProvider
            return MockVideoProvider()

    # 3. Dynamic Model-to-Provider Routing
    model_cap = get_model_capability(model_id)

    if not model_cap.configured or not model_cap.is_available:
        raise ProviderFailureException(
            f"Provider '{model_cap.provider}' for model '{model_cap.name}' is unconfigured or unavailable (Status: {model_cap.status_label}). "
            "Please configure valid API credentials or GPU endpoint in backend/.env"
        )

    provider_name = model_cap.provider.lower()

    if provider_name == "huggingface":
        from app.services.video.huggingface import HuggingFaceVideoProvider
        return HuggingFaceVideoProvider(model=model_cap.id)
    elif provider_name == "fal-ai":
        from app.services.video.fal import FalVideoProvider
        fal_slug = "fal-ai/hunyuan-video" if model_cap.id == "hunyuan-video-v1" else model_cap.id
        return FalVideoProvider(model=fal_slug)
    elif provider_name == "remote_wan":
        from app.services.video.remote_wan import RemoteWanVideoProvider
        return RemoteWanVideoProvider()
    elif provider_name == "wan":
        from app.services.video.wan import WanVideoProvider
        return WanVideoProvider()
    else:
        raise ProviderFailureException(
            f"Model '{model_cap.name}' requires API integration for provider '{model_cap.provider}' which is not configured on this instance."
        )
