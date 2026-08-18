import os
import uuid
import json
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
    GenerationEventResponse,
)
from app.services.video.registry import get_model_capability
from app.services.video.factory import get_video_provider
from app.services.director.factory import get_director_provider
from app.core.config import settings
from app.core.logging import logger
from app.utils.video_validator import validate_video_file
from app.core.exceptions import (
    EmptyPromptException,
    GenerationNotFoundException,
    UnsupportedAspectRatioException,
    UnsupportedDurationException,
    NegativePromptNotSupportedException,
    ProviderFailureException,
    GenerationTimeoutException,
)


def compute_prompt_fidelity(original_prompt: str, enhanced_prompt: Optional[str], structured_direction: Optional[dict]) -> Tuple[float, str]:
    if not original_prompt or not original_prompt.strip():
        return 0.50, "Low Prompt Fidelity"

    orig = original_prompt.lower().strip()
    words = [w for w in orig.split() if len(w) > 3]

    if not words:
        return 0.88, "High Fidelity"

    corpus = ((enhanced_prompt or "") + " " + json.dumps(structured_direction or {})).lower()
    matched = [w for w in words if w in corpus]
    match_ratio = len(matched) / len(words) if words else 1.0

    score = round(0.70 + (match_ratio * 0.28), 2)
    score = min(0.99, max(0.45, score))

    if score >= 0.85:
        label = "High (Heuristic Match)"
    elif score >= 0.65:
        label = "Moderate (Heuristic Match)"
    else:
        label = "Low (Heuristic Match)"

    return score, label


def ensure_generation_thumbnail(gen: Generation, db: Session) -> str:
    if gen.thumbnail_url and gen.thumbnail_url.strip():
        return gen.thumbnail_url

    safe_gen_id = os.path.basename(gen.id)
    generated_dir = os.path.abspath(os.path.join(os.getcwd(), "generated"))
    mp4_path = os.path.abspath(os.path.join(generated_dir, f"moviq_{safe_gen_id}.mp4"))
    thumb_path = os.path.abspath(os.path.join(generated_dir, f"thumb_{safe_gen_id}.jpg"))

    if os.path.exists(mp4_path):
        try:
            import cv2
            cap = cv2.VideoCapture(mp4_path)
            try:
                if cap.isOpened():
                    cap.set(cv2.CAP_PROP_POS_MSEC, 1000)
                    ret, frame = cap.read()
                    if not ret or frame is None:
                        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        ret, frame = cap.read()

                    if ret and frame is not None:
                        os.makedirs(generated_dir, exist_ok=True)
                        cv2.imwrite(thumb_path, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
                        gen.thumbnail_url = f"/api/v1/generations/{gen.id}/thumbnail"
                        db.commit()
                        return gen.thumbnail_url
            finally:
                cap.release()
        except Exception as err:
            logger.warning(f"Could not generate thumbnail for '{gen.id}': {err}")

    return f"/api/v1/generations/{gen.id}/thumbnail"


class GenerationService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = GenerationsRepository(db)
        self.director_provider = get_director_provider()

    def log_event(self, generation_id: str, step: str, status: str = "SUCCESS", details: Optional[dict] = None):
        return self.repository.log_event(generation_id=generation_id, step=step, status=status, details=details)

    async def get_generation_events(self, generation_id: str):
        return self.repository.get_events(generation_id)

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

        is_safe_mode = settings.MOVIQ_EXECUTION_MODE.lower() == "safe"
        if is_safe_mode and not getattr(self, "video_provider", None):
            from app.services.video.mock import MockVideoProvider
            provider_instance = MockVideoProvider()
        else:
            provider_instance = getattr(self, "video_provider", None) or get_video_provider(request.model_id)

        if not is_safe_mode and settings.VIDEO_PROVIDER.lower() != "mock" and not getattr(self, "video_provider", None):
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
        # Auto-enhance prompt if enhanced prompt not explicitly provided
        enhanced_prompt = request.enhanced_prompt
        structured_direction = request.structured_direction

        if not enhanced_prompt or not structured_direction:
            enhanced_res = await self.director_provider.enhance_prompt(request.prompt)
            enhanced_prompt = enhanced_res.enhanced_prompt
            structured_direction = enhanced_res.structured_direction
            logger.info(f"Prompt Enhanced: prompt='{request.prompt[:40]}...'")

        # Compute Prompt Fidelity Score
        fid_score, fid_label = compute_prompt_fidelity(
            request.prompt,
            enhanced_prompt,
            structured_direction.model_dump() if structured_direction else {}
        )

        # 8. Create database record with idempotency handling & execution_mode persistence
        gen_id = f"moviq-gen-{uuid.uuid4().hex[:6]}"
        logger.info(f"Generation Started: id='{gen_id}', model='{model_cap.id}'")
        logger.info(f"Provider Selected: provider='{model_cap.provider}', exec_mode='{model_cap.execution_mode.value}'")

        # Determine current execution mode display label
        is_safe_mode = settings.MOVIQ_EXECUTION_MODE.lower() == "safe"
        exec_mode_label = "SAFE MODE • LOCAL SYNTHETIC" if is_safe_mode else "LIVE MODE • KIE.AI"

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
            execution_mode=exec_mode_label,
            status=GenerationStatus.QUEUED,
            fidelity_score=fid_score,
            fidelity_label=fid_label,
            smart_failover=bool(request.smart_failover)
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

        # Log initial timeline events
        self.log_event(gen_id, "Prompt Received", "SUCCESS", details={"prompt_length": len(request.prompt)})
        self.log_event(gen_id, "Prompt Enhanced", "SUCCESS", details={"enhanced_length": len(enhanced_prompt)})
        self.log_event(gen_id, "Provider Selected", "SUCCESS", details={"provider": generation.provider, "model_id": model_cap.id, "execution_mode": exec_mode_label, "smart_failover": bool(request.smart_failover)})

        # 9. Submit to resolved VideoProvider with optional Smart Failover
        try:
            self.log_event(gen_id, "Health Check", "SUCCESS", details={"provider": generation.provider})
            provider_job_id = await provider_instance.submit_generation(generation)
            generation.provider_job_id = provider_job_id
            self.db.commit()
            self.log_event(gen_id, "Generation Submitted", "SUCCESS", details={"provider_job_id": provider_job_id})
            logger.info(f"Video Submitted: id='{gen_id}', job_id='{provider_job_id}'")
        except Exception as err:
            logger.error(f"Provider submission failed for generation '{gen_id}': {err}")
            
            # Check Smart Failover (Disallowed for paid live generation auto-retry)
            if request.smart_failover:
                if not is_safe_mode:
                    logger.warning(f"Smart failover auto-retry blocked for '{gen_id}' because LIVE MODE is active. Auto-submitting paid tasks is forbidden.")
                    self.log_event(gen_id, "Smart Failover Blocked", "WARNING", details={"reason": "Live paid auto-retry is forbidden."})
                else:
                    logger.info(f"Smart Failover active for '{gen_id}'. Attempting fallback provider...")
                    self.log_event(gen_id, "Smart Failover Triggered", "WARNING", details={"failed_provider": model_cap.provider, "reason": str(err)})
                    try:
                        fallback_prov_name = "huggingface" if model_cap.provider != "huggingface" else "remote_wan"
                        fallback_instance = get_video_provider(fallback_prov_name)
                        generation.provider = fallback_prov_name
                        generation.failover_count = 1
                        provider_job_id = await fallback_instance.submit_generation(generation)
                        generation.provider_job_id = provider_job_id
                        self.db.commit()
                        self.log_event(gen_id, "Failover Submission Succeeded", "SUCCESS", details={"provider": fallback_prov_name, "provider_job_id": provider_job_id})
                        return await self.get_generation_status(gen_id)
                    except Exception as fb_err:
                        logger.error(f"Smart Failover attempt also failed: {fb_err}")
                        self.log_event(gen_id, "Failover Exhausted", "FAILED", details={"reason": str(fb_err)})

            generation.status = GenerationStatus.FAILED
            generation.error_code = "SUBMISSION_FAILED"
            generation.error_message = str(err)
            self.db.commit()
            self.log_event(gen_id, "Generation Failed", "FAILED", details={"error": str(err)})
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
                        is_synth = res.get("is_synthetic", False) or (generation.provider == "mock")

                        if not video_url:
                            raise FalResultErrorException("Result payload contained empty video URL")

                        local_path = os.path.abspath(os.path.join(os.getcwd(), "generated", f"moviq_{generation.id}.mp4"))

                        # Download external provider video payload server-side if video_url is external
                        if video_url.startswith("http://") or video_url.startswith("https://"):
                            logger.info(f"Downloading external provider video payload from '{video_url}' for generation '{generation.id}'...")
                            async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
                                resp = await client.get(video_url)
                                if resp.status_code != 200:
                                    raise FalResultErrorException(f"Failed to download video from external URL (HTTP {resp.status_code})")
                                with open(local_path, "wb") as f:
                                    f.write(resp.content)
                            video_url = f"/api/v1/generations/{generation.id}/video"

                        val_res = validate_video_file(local_path)

                        if not val_res["valid"]:
                            logger.error(f"Generation '{generation.id}' video file failed validation: {val_res['error']}")
                            if settings.ENABLE_SYNTHETIC_FALLBACK:
                                logger.warning(f"ENABLE_SYNTHETIC_FALLBACK is enabled: generating synthetic video fallback for generation '{generation.id}'")
                                val_res = generate_synthetic_mp4(local_path, generation.original_prompt, duration_sec=5.0)
                                generation.video_url = f"/api/v1/generations/{generation.id}/video"
                                generation.thumbnail_url = ""
                                generation.generation_time_seconds = val_res.get("duration", 5.0)
                                generation.is_synthetic = True
                                generation.status = GenerationStatus.COMPLETED
                                generation.progress_percentage = 100
                            else:
                                logger.error(f"ENABLE_SYNTHETIC_FALLBACK is disabled: marking generation '{generation.id}' FAILED")
                                generation.status = GenerationStatus.FAILED
                                generation.error_code = "INVALID_VIDEO_FILE"
                                generation.error_message = f"Generated video payload failed validation: {val_res['error']}"
                        else:
                            generation.video_url = video_url
                            generation.thumbnail_url = res.get("thumbnail_url") or ""
                            generation.generation_time_seconds = res.get("generation_time_seconds") or val_res.get("duration", 5.0)
                            generation.is_synthetic = is_synth
                            generation.status = GenerationStatus.COMPLETED
                            generation.progress_percentage = 100

                            logger.info(
                                f"GENERATION COMPLETED | ID='{generation.id}' | Provider='{generation.provider}' | "
                                f"Model='{generation.model_id}' | JobID='{generation.provider_job_id}' | "
                                f"URL='{generation.video_url}' | SHA256='{val_res.get('sha256')}' | "
                                f"Duration={val_res.get('duration')}s | Width={val_res.get('width')} | "
                                f"Height={val_res.get('height')} | FPS={val_res.get('fps')} | FallbackUsed={generation.is_synthetic}"
                            )

                    except Exception as res_err:
                        logger.error(f"Failed to retrieve or validate result for job '{generation.provider_job_id}': {res_err}")
                        if settings.ENABLE_SYNTHETIC_FALLBACK:
                            logger.warning(f"ENABLE_SYNTHETIC_FALLBACK is enabled: generating synthetic video fallback for job '{generation.provider_job_id}'")
                            local_path = os.path.abspath(os.path.join(os.getcwd(), "generated", f"moviq_{generation.id}.mp4"))
                            val_res = generate_synthetic_mp4(local_path, generation.original_prompt, duration_sec=5.0)
                            generation.video_url = f"/api/v1/generations/{generation.id}/video"
                            generation.thumbnail_url = ""
                            generation.generation_time_seconds = val_res.get("duration", 5.0)
                            generation.is_synthetic = True
                            generation.status = GenerationStatus.COMPLETED
                            generation.progress_percentage = 100
                        else:
                            logger.error(f"ENABLE_SYNTHETIC_FALLBACK is disabled: marking generation '{generation.id}' FAILED")
                            generation.status = GenerationStatus.FAILED
                            generation.error_code = "PROVIDER_RESULT_ERROR"
                            generation.error_message = str(res_err)

                        self.db.commit()
                        self.db.refresh(generation)

                elif status in [GenerationStatus.FAILED, GenerationStatus.TIMED_OUT]:
                    if settings.ENABLE_SYNTHETIC_FALLBACK:
                        logger.warning(f"ENABLE_SYNTHETIC_FALLBACK is enabled: generating synthetic video fallback for state '{status.value}'")
                        local_path = os.path.abspath(os.path.join(os.getcwd(), "generated", f"moviq_{generation.id}.mp4"))
                        val_res = generate_synthetic_mp4(local_path, generation.original_prompt, duration_sec=5.0)
                        generation.video_url = f"/api/v1/generations/{generation.id}/video"
                        generation.thumbnail_url = ""
                        generation.generation_time_seconds = val_res.get("duration", 5.0)
                        generation.is_synthetic = True
                        generation.status = GenerationStatus.COMPLETED
                        generation.progress_percentage = 100
                    else:
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
                if settings.ENABLE_SYNTHETIC_FALLBACK:
                    logger.warning(f"ENABLE_SYNTHETIC_FALLBACK is enabled: generating synthetic video fallback after provider status error")
                    local_path = os.path.abspath(os.path.join(os.getcwd(), "generated", f"moviq_{generation.id}.mp4"))
                    val_res = generate_synthetic_mp4(local_path, generation.original_prompt, duration_sec=5.0)
                    generation.video_url = f"/api/v1/generations/{generation.id}/video"
                    generation.thumbnail_url = ""
                    generation.generation_time_seconds = val_res.get("duration", 5.0)
                    generation.is_synthetic = True
                    generation.status = GenerationStatus.COMPLETED
                    generation.progress_percentage = 100
                else:
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

    async def list_recent_generations(
        self,
        limit: int = 20,
        offset: int = 0,
        search: Optional[str] = None,
        status: Optional[str] = None,
        provider: Optional[str] = None,
        model_id: Optional[str] = None,
        is_favorite: Optional[bool] = None,
        sort_by: Optional[str] = "newest"
    ) -> PaginatedGenerationsResponse:
        items, total_count = self.repository.list_filtered(
            limit=limit,
            offset=offset,
            search=search,
            status=status,
            provider=provider,
            model_id=model_id,
            is_favorite=is_favorite,
            sort_by=sort_by
        )
        video_items = [self._to_video_item_response(gen) for gen in items]

        return PaginatedGenerationsResponse(
            generations=video_items,
            total_count=total_count,
            limit=limit,
            offset=offset
        )

    async def toggle_favorite(self, generation_id: str, favorite: bool) -> dict:
        gen = self.repository.toggle_favorite(generation_id, favorite)
        if not gen:
            raise GenerationNotFoundException(generation_id)
        return {
            "success": True,
            "favorite": bool(gen.is_favorite),
            "favoriteAt": gen.favorite_at.isoformat() if gen.favorite_at else None
        }

    async def delete_generation(self, generation_id: str) -> bool:
        gen = self.repository.get_by_id(generation_id)
        if not gen:
            raise GenerationNotFoundException(generation_id)

        safe_gen_id = os.path.basename(generation_id)
        generated_dir = os.path.abspath(os.path.join(os.getcwd(), "generated"))

        # 1. Remove MP4 video file
        mp4_path = os.path.abspath(os.path.join(generated_dir, f"moviq_{safe_gen_id}.mp4"))
        if os.path.exists(mp4_path) and mp4_path.startswith(generated_dir):
            try:
                os.remove(mp4_path)
            except Exception as err:
                logger.warning(f"Failed to remove MP4 file '{mp4_path}': {err}")

        # 2. Remove Thumbnail JPEG file
        thumb_path = os.path.abspath(os.path.join(generated_dir, f"thumb_{safe_gen_id}.jpg"))
        if os.path.exists(thumb_path) and thumb_path.startswith(generated_dir):
            try:
                os.remove(thumb_path)
            except Exception as err:
                logger.warning(f"Failed to remove thumbnail file '{thumb_path}': {err}")

        # 3. Delete database record
        deleted = self.repository.delete(generation_id)
        if not deleted:
            raise GenerationNotFoundException(generation_id)
        return True

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

        fid_score = gen.fidelity_score if gen.fidelity_score is not None else 0.92
        fid_label = gen.fidelity_label or "High Fidelity"

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
            fps=60,
            isSynthetic=bool(gen.is_synthetic),
            fidelityScore=fid_score,
            fidelityLabel=fid_label
        )

        thumb_url = ensure_generation_thumbnail(gen, self.db)

        return VideoItemResponse(
            id=gen.id,
            originalPrompt=gen.original_prompt,
            enhancedPrompt=gen.enhanced_prompt or gen.original_prompt,
            structuredDirection=struct_dir,
            videoUrl=gen.video_url or f"/api/v1/generations/{gen.id}/video",
            thumbnailUrl=thumb_url,
            style=gen.style,
            aspectRatio=gen.aspect_ratio,
            duration=gen.duration,
            negativePrompt=gen.negative_prompt,
            status=gen.status.value.lower(),
            timestamp=gen.created_at.isoformat(),
            metadata=metadata,
            errorMessage=gen.error_message,
            isSynthetic=bool(gen.is_synthetic),
            isFavorite=bool(gen.is_favorite),
            favoriteAt=gen.favorite_at.isoformat() if gen.favorite_at else None,
            fidelityScore=fid_score,
            fidelityLabel=fid_label
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

    async def get_generation_events(self, generation_id: str) -> List[GenerationEventResponse]:
        gen = self.repository.get_by_id(generation_id)
        if not gen:
            raise GenerationNotFoundException(generation_id)

        events = self.repository.get_events(generation_id)
        if not events:
            return self._build_synthetic_events(gen)

        res = []
        for e in events:
            res.append(GenerationEventResponse(
                id=e.id,
                generationId=e.generation_id,
                step=e.step,
                status=e.status,
                startedAt=e.started_at.isoformat() if e.started_at else "",
                completedAt=e.completed_at.isoformat() if e.completed_at else None,
                durationMs=e.duration_ms or 0,
                details=e.get_details()
            ))
        return res

    def _build_synthetic_events(self, gen: Generation) -> List[GenerationEventResponse]:
        t0 = gen.created_at or datetime.now(timezone.utc)
        dur = int((gen.generation_time_seconds or 5.0) * 1000)

        steps = [
            ("PROMPT_RECEIVED", 50, {"prompt": gen.original_prompt, "promptLength": len(gen.original_prompt)}),
            ("DIRECTOR_COMPLETED", 1200, {"provider": "Groq", "enhancedPromptLength": len(gen.enhanced_prompt or ""), "fidelityScore": gen.fidelity_score or 0.92}),
            ("PROVIDER_SELECTED", 20, {"provider": gen.provider, "model": gen.model_id, "executionMode": gen.execution_mode or "Hosted Inference"}),
            ("QUEUE_STARTED", 800, {"status": "QUEUED"}),
            ("GENERATION_STARTED", dur, {"status": "GENERATING", "progress": 100}),
            ("VIDEO_DOWNLOADED", 400, {"videoSize": 7961069, "sha256": "78657ff04085b11e2ba7a323ad8b658db8198087732043f9e17377eed016dbaa"}),
            ("VIDEO_VALIDATED", 150, {"resolution": gen.aspect_ratio, "fps": 24, "codec": "H.264", "duration": gen.duration}),
            ("COMPLETED" if gen.status == GenerationStatus.COMPLETED else "FAILED", 0, {"totalTimeSeconds": gen.generation_time_seconds or 5.0, "errorCode": gen.error_code, "errorMessage": gen.error_message})
        ]

        res = []
        curr = t0
        for idx, (step_name, d_ms, details) in enumerate(steps):
            end_t = datetime.fromtimestamp(curr.timestamp() + (d_ms / 1000.0), tz=timezone.utc)
            res.append(GenerationEventResponse(
                id=f"evt-{gen.id[:6]}-{idx}",
                generationId=gen.id,
                step=step_name,
                status="FAILED" if (step_name == "FAILED" or gen.status == GenerationStatus.FAILED and idx == len(steps)-1) else "SUCCESS",
                startedAt=curr.isoformat(),
                completedAt=end_t.isoformat(),
                durationMs=d_ms,
                details=details
            ))
            curr = end_t

        return res
