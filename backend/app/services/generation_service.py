import uuid
from typing import Tuple, List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.generation import Generation
from app.db.repositories.generations import GenerationsRepository
from app.schemas.common import GenerationStatus, AspectRatio, Duration
from app.schemas.director import StructuredDirection
from app.schemas.generation import (
    CreateGenerationRequest,
    GenerationStatusResponse,
    VideoItemResponse,
    GenerationMetadataResponse,
    GenerationProgressInfoResponse,
    PaginatedGenerationsResponse,
)
from app.services.video.registry import get_model_capability
from app.services.video.factory import get_video_provider
from app.services.director.factory import get_director_provider
from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import (
    EmptyPromptException,
    GenerationNotFoundException,
    UnsupportedAspectRatioException,
    UnsupportedDurationException,
    NegativePromptNotSupportedException,
    ProviderFailureException,
    GenerationTimeoutException,
    FalResultErrorException,
)


class GenerationService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = GenerationsRepository(db)
        self.director_provider = get_director_provider()

    async def create_generation(
        self,
        request: CreateGenerationRequest,
        idempotency_key: Optional[str] = None
    ) -> GenerationStatusResponse:
        # 0. Check Idempotency Key
        if idempotency_key:
            existing = self.repository.get_by_idempotency_key(idempotency_key)
            if existing:
                logger.info(f"Idempotency match found for key '{idempotency_key}'. Returning existing generation '{existing.id}'")
                return await self.get_generation_status(existing.id)

        # 1. Validate prompt
        if not request.prompt or not request.prompt.strip():
            raise EmptyPromptException()

        # 2. Validate model capabilities & configuration
        model_cap = get_model_capability(request.model_id)

        # Allow test mock instance override or mock settings
        provider_instance = getattr(self, "video_provider", None) or get_video_provider(request.model_id)

        if settings.VIDEO_PROVIDER.lower() != "mock" and not getattr(self, "video_provider", None):
            if not model_cap.configured or not model_cap.is_available:
                raise ProviderFailureException(
                    f"Model '{model_cap.name}' is unconfigured or unavailable (Status: {model_cap.status_label}). "
                    "Please configure valid provider credentials in backend/.env."
                )

        # 4. Validate aspect ratio
        if request.aspect_ratio not in model_cap.supported_aspect_ratios:
            raise UnsupportedAspectRatioException(request.aspect_ratio.value, request.model_id)

        # 5. Validate duration
        if request.duration not in model_cap.supported_durations:
            raise UnsupportedDurationException(request.duration.value, request.model_id)

        # 6. Validate negative prompt
        if request.negative_prompt and not model_cap.supports_negative_prompt:
            raise NegativePromptNotSupportedException(request.model_id)

        # 7. Auto-enhance prompt if enhanced prompt not explicitly provided
        enhanced_prompt = request.enhanced_prompt
        structured_direction = request.structured_direction

        if not enhanced_prompt or not structured_direction:
            enhanced_res = await self.director_provider.enhance_prompt(request.prompt)
            enhanced_prompt = enhanced_res.enhanced_prompt
            structured_direction = enhanced_res.structured_direction

        # 8. Create database record with idempotency handling & execution_mode persistence
        gen_id = f"moviq-gen-{uuid.uuid4().hex[:6]}"
        generation = Generation(
            id=gen_id,
            idempotency_key=idempotency_key,
            original_prompt=request.prompt,
            enhanced_prompt=enhanced_prompt,
            negative_prompt=request.negative_prompt,
            style=request.style.value,
            aspect_ratio=request.aspect_ratio.value,
            duration=request.duration.value,
            provider=model_cap.provider,
            model_id=model_cap.id,
            execution_mode=model_cap.execution_mode.value,
            status=GenerationStatus.QUEUED,
        )
        generation.set_structured_direction(structured_direction.model_dump())

        try:
            self.repository.create(generation)
        except IntegrityError:
            self.db.rollback()
            if idempotency_key:
                existing = self.repository.get_by_idempotency_key(idempotency_key)
                if existing:
                    logger.info(f"Race condition handled for key '{idempotency_key}'. Returning generation '{existing.id}'")
                    return await self.get_generation_status(existing.id)
            raise

        # 9. Submit to resolved VideoProvider
        try:
            provider_job_id = await provider_instance.submit_generation(generation)
            generation.provider_job_id = provider_job_id
            self.db.commit()
        except Exception as err:
            logger.error(f"Provider submission failed for generation '{gen_id}': {err}")
            generation.status = GenerationStatus.FAILED
            generation.error_code = "SUBMISSION_FAILED"
            generation.error_message = str(err)
            self.db.commit()
            raise err

        return await self.get_generation_status(gen_id)

    async def get_generation_status(self, generation_id: str) -> GenerationStatusResponse:
        generation = self.repository.get_by_id(generation_id)
        if not generation:
            raise GenerationNotFoundException(generation_id)

        # Timeout checking (configurable GENERATION_TIMEOUT_SECONDS = 600)
        if generation.status not in [GenerationStatus.COMPLETED, GenerationStatus.FAILED, GenerationStatus.TIMED_OUT]:
            now = datetime.now(timezone.utc)
            created_at_utc = generation.created_at
            if created_at_utc.tzinfo is None:
                created_at_utc = created_at_utc.replace(tzinfo=timezone.utc)
            elapsed_seconds = (now - created_at_utc).total_seconds()

            if elapsed_seconds > settings.GENERATION_TIMEOUT_SECONDS:
                logger.warn(f"Generation '{generation_id}' exceeded overall AI timeout limit of {settings.GENERATION_TIMEOUT_SECONDS}s")
                generation.status = GenerationStatus.TIMED_OUT
                generation.error_code = "GENERATION_TIMEOUT"
                generation.error_message = f"Generation timed out after {int(elapsed_seconds)} seconds"
                self.db.commit()

        # Sync status from VideoProvider if active
        if generation.provider_job_id and generation.status not in [
            GenerationStatus.COMPLETED,
            GenerationStatus.FAILED,
            GenerationStatus.TIMED_OUT,
        ]:
            try:
                video_provider = getattr(self, "video_provider", None) or get_video_provider(generation.model_id)
                status, pct = await video_provider.check_status(generation.provider_job_id)

                if status == GenerationStatus.COMPLETED and not generation.video_url:
                    generation.status = GenerationStatus.PROCESSING
                    generation.progress_percentage = 95
                    self.db.commit()

                    try:
                        res = await video_provider.get_result(generation.provider_job_id)
                        video_url = res.get("video_url", "")
                        
                        if not video_url or not (video_url.startswith("http://") or video_url.startswith("https://") or video_url.startswith("/api/v1/")):
                            raise FalResultErrorException("Result payload contained invalid video URL")

                        generation.video_url = video_url
                        generation.thumbnail_url = res.get("thumbnail_url") or "https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?auto=format&fit=crop&w=1200&q=80"
                        generation.generation_time_seconds = res.get("generation_time_seconds", 4.8)
                        generation.status = GenerationStatus.COMPLETED
                        generation.progress_percentage = 100

                    except Exception as res_err:
                        logger.error(f"Failed to retrieve or validate result for job '{generation.provider_job_id}': {res_err}")
                        generation.status = GenerationStatus.FAILED
                        generation.error_code = "PROVIDER_RESULT_ERROR"
                        generation.error_message = str(res_err)

                elif status in [GenerationStatus.FAILED, GenerationStatus.TIMED_OUT]:
                    generation.status = status
                    generation.error_code = status.value
                    generation.error_message = f"Generation process ended with state {status.value}"

                else:
                    generation.status = status
                    generation.progress_percentage = pct

                self.db.commit()
                self.db.refresh(generation)
            except Exception as err:
                logger.error(f"Error checking status for provider job '{generation.provider_job_id}': {err}")
                generation.status = GenerationStatus.FAILED
                generation.error_code = getattr(err, "code", "PROVIDER_ERROR")
                generation.error_message = getattr(err, "message", str(err))
                self.db.commit()
                self.db.refresh(generation)

        # Map to response schema
        if generation.status == GenerationStatus.COMPLETED:
            video_item = self._to_video_item_response(generation)
            return GenerationStatusResponse(id=generation.id, state=generation.status, video=video_item)

        # Active progress info
        progress_info = GenerationProgressInfoResponse(
            state=generation.status,
            current_step_index=self._get_step_index(generation.status),
            total_steps=5,
            step_title=self._get_step_title(generation.status),
            step_description=self._get_step_desc(generation.status),
            percentage=generation.progress_percentage if generation.status in [GenerationStatus.GENERATING, GenerationStatus.PROCESSING] else None,
            is_determinate=generation.status in [GenerationStatus.GENERATING, GenerationStatus.PROCESSING],
            estimated_remaining_seconds=4
        )

        return GenerationStatusResponse(
            id=generation.id,
            state=generation.status,
            progress=progress_info,
            error_message=generation.error_message
        )

    async def list_recent_generations(self, limit: int = 5, offset: int = 0) -> PaginatedGenerationsResponse:
        items, total_count = self.repository.list_recent(limit=limit, offset=offset)
        video_items = [self._to_video_item_response(gen) for gen in items]

        return PaginatedGenerationsResponse(
            generations=video_items,
            total_count=total_count,
            limit=limit,
            offset=offset
        )

    async def retry_generation(self, generation_id: str) -> GenerationStatusResponse:
        original = self.repository.get_by_id(generation_id)
        if not original:
            raise GenerationNotFoundException(generation_id)

        retry_req = CreateGenerationRequest(
            prompt=original.original_prompt,
            enhancedPrompt=original.enhanced_prompt,
            structuredDirection=StructuredDirection(**original.get_structured_direction()),
            style=original.style,
            aspectRatio=original.aspect_ratio,
            duration=original.duration,
            negativePrompt=original.negative_prompt,
            modelId=original.model_id
        )
        return await self.create_generation(retry_req)

    async def create_variation(self, generation_id: str) -> GenerationStatusResponse:
        original = self.repository.get_by_id(generation_id)
        if not original:
            raise GenerationNotFoundException(generation_id)

        var_prompt = f"{original.original_prompt} (Variation: camera angle shift)"
        var_req = CreateGenerationRequest(
            prompt=var_prompt,
            enhancedPrompt=f"{original.enhanced_prompt} [Variation camera angle]",
            structuredDirection=StructuredDirection(**original.get_structured_direction()),
            style=original.style,
            aspectRatio=original.aspect_ratio,
            duration=original.duration,
            negativePrompt=original.negative_prompt,
            modelId=original.model_id
        )
        res = await self.create_generation(var_req)

        new_gen = self.repository.get_by_id(res.id)
        if new_gen:
            new_gen.parent_generation_id = original.id
            self.db.commit()

        return res

    def _to_video_item_response(self, gen: Generation) -> VideoItemResponse:
        direction = gen.get_structured_direction()
        struct_dir = StructuredDirection(
            subject=direction.get("subject", gen.original_prompt),
            environment=direction.get("environment", "Cinematic environment"),
            action=direction.get("action", "Dynamic motion"),
            camera=direction.get("camera", "Cinematic camera angle"),
            lighting=direction.get("lighting", "Volumetric lighting"),
            mood=direction.get("mood", "Sophisticated & modern")
        )

        exec_mode = gen.execution_mode
        if not exec_mode:
            try:
                exec_mode = get_model_capability(gen.model_id).execution_mode.value
            except Exception:
                exec_mode = "Hosted Inference"

        metadata = GenerationMetadataResponse(
            id=f"meta-{gen.id}",
            model=gen.model_id,
            provider=gen.provider,
            executionMode=exec_mode,
            style=gen.style,
            aspectRatio=gen.aspect_ratio,
            duration=gen.duration,
            generationTimeSeconds=gen.generation_time_seconds or 4.8,
            createdAt=gen.created_at.strftime("%Y-%m-%d %H:%M"),
            resolution="1920 × 1080" if gen.aspect_ratio == "16:9" else "1080 × 1920" if gen.aspect_ratio == "9:16" else "1080 × 1080",
            fps=60
        )

        return VideoItemResponse(
            id=gen.id,
            originalPrompt=gen.original_prompt,
            enhancedPrompt=gen.enhanced_prompt,
            structuredDirection=struct_dir,
            videoUrl=gen.video_url or "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
            thumbnailUrl=gen.thumbnail_url or "https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?auto=format&fit=crop&w=1200&q=80",
            style=gen.style,
            aspectRatio=gen.aspect_ratio,
            duration=gen.duration,
            negativePrompt=gen.negative_prompt,
            status=gen.status.value.lower(),
            timestamp="Just now",
            metadata=metadata,
            errorMessage=gen.error_message
        )

    def _get_step_index(self, status: GenerationStatus) -> int:
        mapping = {
            GenerationStatus.QUEUED: 1,
            GenerationStatus.ENHANCING: 2,
            GenerationStatus.SUBMITTED: 3,
            GenerationStatus.GENERATING: 4,
            GenerationStatus.PROCESSING: 5,
            GenerationStatus.COMPLETED: 5,
            GenerationStatus.FAILED: 1,
            GenerationStatus.TIMED_OUT: 1,
        }
        return mapping.get(status, 1)

    def _get_step_title(self, status: GenerationStatus) -> str:
        mapping = {
            GenerationStatus.QUEUED: "Analyzing idea",
            GenerationStatus.ENHANCING: "Enhancing direction",
            GenerationStatus.SUBMITTED: "In Provider Queue",
            GenerationStatus.GENERATING: "Generating video",
            GenerationStatus.PROCESSING: "Validating output",
            GenerationStatus.COMPLETED: "Generation complete",
            GenerationStatus.FAILED: "Generation failed",
            GenerationStatus.TIMED_OUT: "Generation timed out",
        }
        return mapping.get(status, "Processing")

    def _get_step_desc(self, status: GenerationStatus) -> str:
        mapping = {
            GenerationStatus.QUEUED: "Deconstructing prompt & lighting parameters",
            GenerationStatus.ENHANCING: "Building AI Director camera keyframes & mood map",
            GenerationStatus.SUBMITTED: "Job submitted to AI video provider",
            GenerationStatus.GENERATING: "Rendering video diffusion frames",
            GenerationStatus.PROCESSING: "Retrieving and validating video stream payload",
            GenerationStatus.COMPLETED: "Video rendered and available for playback",
            GenerationStatus.FAILED: "Model provider error",
            GenerationStatus.TIMED_OUT: "Provider request timeout",
        }
        return mapping.get(status, "Processing video pipeline")
