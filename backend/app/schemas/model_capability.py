from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.common import AspectRatio, Duration


class ExecutionMode(str, Enum):
    HOSTED_INFERENCE = "Hosted Inference"
    HOSTED_API = "Hosted API"
    SELF_HOSTED = "Self-Hosted GPU"
    EXTERNAL_WEB = "External Web"
    MOCK = "Simulation / Demo"


class ModelCapability(BaseModel):
    id: str
    name: str
    provider: str
    execution_mode: ExecutionMode = Field(default=ExecutionMode.HOSTED_INFERENCE, alias="executionMode")
    tag: str
    description: str
    supported_aspect_ratios: List[AspectRatio] = Field(alias="supportedAspectRatios")
    supported_durations: List[Duration] = Field(alias="supportedDurations")
    supports_negative_prompt: bool = Field(alias="supportsNegativePrompt")
    max_duration_seconds: Optional[int] = Field(default=10, alias="maxDurationSeconds")
    render_profile_description: Optional[str] = Field(default=None, alias="renderProfileDescription")
    is_available: bool = Field(default=True, alias="isAvailable")
    configured: bool = Field(default=True, alias="configured")
    status_label: str = Field(default="READY", alias="statusLabel")
    external_url: Optional[str] = Field(default=None, alias="externalUrl")

    model_config = ConfigDict(populate_by_name=True)


class ModelsResponse(BaseModel):
    models: List[ModelCapability]
