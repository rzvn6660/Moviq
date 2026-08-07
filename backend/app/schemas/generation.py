from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.common import GenerationStatus, StylePreset, AspectRatio, Duration
from app.schemas.director import StructuredDirection


class CreateGenerationRequest(BaseModel):
    prompt: str
    enhanced_prompt: Optional[str] = Field(default=None, alias="enhancedPrompt")
    structured_direction: Optional[StructuredDirection] = Field(default=None, alias="structuredDirection")
    style: StylePreset = StylePreset.CINEMATIC
    aspect_ratio: AspectRatio = Field(default=AspectRatio.SIXTEEN_NINE, alias="aspectRatio")
    duration: Duration = Duration.FIVE_S
    negative_prompt: Optional[str] = Field(default=None, alias="negativePrompt")
    model_id: str = Field(default="Wan-AI/Wan2.2-TI2V-5B", alias="modelId")
    smart_failover: Optional[bool] = Field(default=False, alias="smartFailover")

    model_config = ConfigDict(populate_by_name=True)


class GenerationMetadataResponse(BaseModel):
    id: str
    model: str
    provider: str
    execution_mode: Optional[str] = Field(default="Hosted Inference", alias="executionMode")
    style: StylePreset
    aspect_ratio: AspectRatio = Field(alias="aspectRatio")
    duration: Duration
    generation_time_seconds: float = Field(alias="generationTimeSeconds")
    created_at: str = Field(alias="createdAt")
    resolution: str
    fps: int
    is_synthetic: bool = Field(default=False, alias="isSynthetic")
    fidelity_score: Optional[float] = Field(default=0.92, alias="fidelityScore")
    fidelity_label: Optional[str] = Field(default="High Fidelity", alias="fidelityLabel")

    model_config = ConfigDict(populate_by_name=True)


class VideoItemResponse(BaseModel):
    id: str
    original_prompt: str = Field(alias="originalPrompt")
    enhanced_prompt: str = Field(alias="enhancedPrompt")
    structured_direction: StructuredDirection = Field(alias="structuredDirection")
    video_url: str = Field(alias="videoUrl")
    thumbnail_url: str = Field(alias="thumbnailUrl")
    style: StylePreset
    aspect_ratio: AspectRatio = Field(alias="aspectRatio")
    duration: Duration
    negative_prompt: Optional[str] = Field(default=None, alias="negativePrompt")
    status: str
    timestamp: str
    metadata: GenerationMetadataResponse
    error_message: Optional[str] = Field(default=None, alias="errorMessage")
    is_synthetic: bool = Field(default=False, alias="isSynthetic")
    is_favorite: bool = Field(default=False, alias="isFavorite")
    favorite_at: Optional[str] = Field(default=None, alias="favoriteAt")
    fidelity_score: Optional[float] = Field(default=0.92, alias="fidelityScore")
    fidelity_label: Optional[str] = Field(default="High Fidelity", alias="fidelityLabel")

    model_config = ConfigDict(populate_by_name=True)


class GenerationEventResponse(BaseModel):
    id: str
    generation_id: str = Field(alias="generationId")
    step: str
    status: str
    started_at: str = Field(alias="startedAt")
    completed_at: Optional[str] = Field(default=None, alias="completedAt")
    duration_ms: Optional[int] = Field(default=0, alias="durationMs")
    details: Optional[dict] = Field(default_factory=dict)

    model_config = ConfigDict(populate_by_name=True)


class ToggleFavoriteRequest(BaseModel):
    favorite: bool


class GenerationProgressInfoResponse(BaseModel):
    state: GenerationStatus
    current_step_index: int = Field(alias="currentStepIndex")
    total_steps: int = Field(alias="totalSteps")
    step_title: str = Field(alias="stepTitle")
    step_description: str = Field(alias="stepDescription")
    percentage: Optional[int] = None
    is_determinate: bool = Field(alias="isDeterminate")
    estimated_remaining_seconds: Optional[int] = Field(default=None, alias="estimatedRemainingSeconds")

    model_config = ConfigDict(populate_by_name=True)


class GenerationStatusResponse(BaseModel):
    id: str
    state: GenerationStatus
    video: Optional[VideoItemResponse] = None
    progress: Optional[GenerationProgressInfoResponse] = None
    error_message: Optional[str] = Field(default=None, alias="errorMessage")

    model_config = ConfigDict(populate_by_name=True)


class PaginatedGenerationsResponse(BaseModel):
    generations: List[VideoItemResponse]
    total_count: int = Field(alias="totalCount")
    limit: int
    offset: int

    model_config = ConfigDict(populate_by_name=True)
