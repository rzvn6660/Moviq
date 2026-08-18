from typing import Optional
from app.services.video.base import BaseVideoProvider
from app.services.video.registry import get_model_capability
from app.core.config import settings
from app.core.exceptions import ProviderFailureException


def get_video_provider(model_id: Optional[str] = None) -> BaseVideoProvider:
    """
    Moviq v2.0 Deterministic Provider Factory.
    Routes generation requests deterministically to one of the 6 supported production providers:
    [Kie.ai, Luma AI, Hailuo AI, Hugging Face, Remote Wan, LTX Video].
    Never silently changes provider or substitutes models.
    """
    # 1. Global mock override for testing
    if settings.VIDEO_PROVIDER.lower() == "mock":
        from app.services.video.mock import MockVideoProvider
        return MockVideoProvider()

    # 2. Default provider resolution if model_id is omitted
    if not model_id:
        prov = settings.VIDEO_PROVIDER.lower()
        if prov == "kie":
            from app.services.video.kie import KieVideoProvider
            return KieVideoProvider()
        elif prov == "luma":
            from app.services.video.luma import LumaVideoProvider
            return LumaVideoProvider()
        elif prov == "hailuo":
            from app.services.video.hailuo import HailuoVideoProvider
            return HailuoVideoProvider()
        elif prov in ("huggingface", "hf"):
            from app.services.video.huggingface import HuggingFaceVideoProvider
            return HuggingFaceVideoProvider()
        elif prov in ("remote_wan", "remote-wan"):
            from app.services.video.remote_wan import RemoteWanVideoProvider
            return RemoteWanVideoProvider()
        elif prov == "ltx":
            from app.services.video.ltx import LTXVideoProvider
            return LTXVideoProvider()
        else:
            from app.services.video.kie import KieVideoProvider
            return KieVideoProvider()

    # 3. Dynamic Model-to-Provider Deterministic Routing
    model_cap = get_model_capability(model_id)
    provider_name = model_cap.provider.lower()

    if provider_name == "kie":
        from app.services.video.kie import KieVideoProvider
        return KieVideoProvider(model=model_cap.id)
    elif provider_name == "luma":
        from app.services.video.luma import LumaVideoProvider
        return LumaVideoProvider()
    elif provider_name == "hailuo":
        from app.services.video.hailuo import HailuoVideoProvider
        return HailuoVideoProvider()
    elif provider_name == "huggingface":
        from app.services.video.huggingface import HuggingFaceVideoProvider
        return HuggingFaceVideoProvider(model=model_cap.id)
    elif provider_name == "remote_wan":
        from app.services.video.remote_wan import RemoteWanVideoProvider
        return RemoteWanVideoProvider()
    elif provider_name == "ltx":
        from app.services.video.ltx import LTXVideoProvider
        return LTXVideoProvider()
    else:
        raise ProviderFailureException(
            f"Model '{model_cap.name}' requires provider '{model_cap.provider}' which is not supported in Moviq v2.0."
        )
