from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.common import AspectRatio, Duration


class ModelCapability(BaseModel):
    id: str
    name: str
    provider: str
    tag: str
    description: str
    supported_aspect_ratios: List[AspectRatio] = Field(alias="supportedAspectRatios")
    supported_durations: List[Duration] = Field(alias="supportedDurations")
    supports_negative_prompt: bool = Field(alias="supportsNegativePrompt")
    max_duration_seconds: Optional[int] = Field(default=10, alias="maxDurationSeconds")
    render_profile_description: Optional[str] = Field(default=None, alias="renderProfileDescription")
    is_available: bool = Field(default=True, alias="isAvailable")

    model_config = ConfigDict(populate_by_name=True)


class ModelsResponse(BaseModel):
    models: List[ModelCapability]
