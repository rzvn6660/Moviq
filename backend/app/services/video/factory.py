from app.services.video.base import VideoProvider
from app.core.config import settings


def get_video_provider() -> VideoProvider:
    provider_name = settings.VIDEO_PROVIDER.lower()
    if provider_name == "fal":
        from app.services.video.fal import FalVideoProvider
        return FalVideoProvider()
    elif provider_name == "huggingface":
        from app.services.video.huggingface import HuggingFaceVideoProvider
        return HuggingFaceVideoProvider()
    elif provider_name == "wan":
        from app.services.video.wan import WanVideoProvider
        return WanVideoProvider()
    else:
        from app.services.video.mock import MockVideoProvider
        return MockVideoProvider()
