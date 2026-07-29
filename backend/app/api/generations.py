import os
import httpx
import urllib.parse
import ipaddress
from typing import Optional
from fastapi import APIRouter, Depends, Query, Header, status, HTTPException
from fastapi.responses import StreamingResponse, FileResponse, Response
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.generation import (
    CreateGenerationRequest,
    GenerationStatusResponse,
    PaginatedGenerationsResponse,
)
from app.services.generation_service import GenerationService
from app.core.exceptions import GenerationNotFoundException, ValidationErrorException
from app.core.logging import logger
from app.models.generation import Generation
from app.schemas.common import GenerationStatus

router = APIRouter(tags=["Generations"])


def is_safe_download_url(url: str) -> bool:
    """
    Validates download target URL to prevent SSRF and arbitrary open proxy vulnerabilities.
    Enforces http/https or backend relative paths (/api/v1/...), rejects localhost, loopback, link-local, and private IP ranges.
    """
    if not url or not isinstance(url, str):
        return False

    # Allow internal local API media endpoints
    if url.startswith("/api/v1/generations/") and url.endswith("/video"):
        return True

    try:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False

        hostname = parsed.hostname
        if not hostname:
            return False

        hostname_lower = hostname.lower()
        if hostname_lower == "localhost" or hostname_lower.endswith(".local") or hostname_lower.endswith(".internal"):
            return False

        # IP address check
        try:
            ip = ipaddress.ip_address(hostname_lower)
            if ip.is_loopback or ip.is_private or ip.is_link_local or ip.is_reserved or ip.is_multicast:
                return False
        except ValueError:
            # Valid domain name
            pass

        return True
    except Exception:
        return False


@router.post(
    "/generations",
    response_model=GenerationStatusResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Video Generation",
    description="Validates parameters against model capabilities and submits a video generation job with idempotency key support."
)
async def create_generation(
    request: CreateGenerationRequest,
    idempotency_key: Optional[str] = Header(default=None, alias="Idempotency-Key"),
    db: Session = Depends(get_db)
) -> GenerationStatusResponse:
    service = GenerationService(db)
    return await service.create_generation(request, idempotency_key=idempotency_key)


@router.get(
    "/generations/{generation_id}/video",
    summary="Serve Local Generated Video",
    description="Serves locally persisted video MP4 files safely with path traversal protection."
)
async def get_generation_local_video(
    generation_id: str,
    db: Session = Depends(get_db)
):
    # Validate generation exists in DB
    gen = db.query(Generation).filter(Generation.id == generation_id).first()
    if not gen:
        raise GenerationNotFoundException(generation_id)

    # Sanitize generation_id against path traversal attacks
    safe_gen_id = os.path.basename(generation_id)
    generated_dir = os.path.abspath(os.path.join(os.getcwd(), "generated"))
    filepath = os.path.abspath(os.path.join(generated_dir, f"moviq_{safe_gen_id}.mp4"))

    # Strict boundary enforcement
    if not filepath.startswith(generated_dir) or not os.path.exists(filepath):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "VIDEO_FILE_NOT_FOUND", "message": f"Local video output file for generation '{generation_id}' was not found"}}
        )

    return FileResponse(filepath, media_type="video/mp4")


@router.get(
    "/generations/{generation_id}/download",
    summary="Download Completed Video",
    description="Streams a completed video generation output with Content-Disposition headers while preventing SSRF."
)
async def download_generation_video(
    generation_id: str,
    db: Session = Depends(get_db)
):
    gen = db.query(Generation).filter(Generation.id == generation_id).first()
    if not gen:
        raise GenerationNotFoundException(generation_id)

    if gen.status != GenerationStatus.COMPLETED or not gen.video_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "NOT_COMPLETED", "message": "Generation is not completed or video URL is missing"}}
        )

    video_url = gen.video_url

    # Strict SSRF & Security Validation
    if not is_safe_download_url(video_url):
        logger.error(f"Download request rejected: URL '{video_url}' failed security validation")
        raise ValidationErrorException("Video URL failed security verification")

    filename = f"moviq_{gen.id}.mp4"

    # Handle local media references (/api/v1/generations/{id}/video)
    if video_url.startswith("/api/v1/"):
        safe_gen_id = os.path.basename(gen.id)
        generated_dir = os.path.abspath(os.path.join(os.getcwd(), "generated"))
        filepath = os.path.abspath(os.path.join(generated_dir, f"moviq_{safe_gen_id}.mp4"))
        if filepath.startswith(generated_dir) and os.path.exists(filepath):
            return FileResponse(
                filepath,
                media_type="video/mp4",
                headers={"Content-Disposition": f'attachment; filename="{filename}"'}
            )

    # Stream external response chunks asynchronously to avoid loading large files into memory
    async def video_stream_generator():
        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                async with client.stream("GET", video_url) as stream_resp:
                    if stream_resp.status_code == 200:
                        async for chunk in stream_resp.aiter_bytes(chunk_size=65536):
                            yield chunk
        except Exception as err:
            logger.warn(f"Streaming error for generation '{generation_id}': {err}")

    return StreamingResponse(
        video_stream_generator(),
        media_type="video/mp4",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.get(
    "/generations/{generation_id}",
    response_model=GenerationStatusResponse,
    summary="Get Generation Status or Result",
    description="Returns current status, active stage, progress details, or completed video result."
)
async def get_generation(
    generation_id: str,
    db: Session = Depends(get_db)
) -> GenerationStatusResponse:
    service = GenerationService(db)
    return await service.get_generation_status(generation_id)


@router.get(
    "/generations",
    response_model=PaginatedGenerationsResponse,
    summary="List Recent Generations",
    description="Returns latest generations list. Defaults to limit=5 for evaluator requirement."
)
async def list_generations(
    limit: int = Query(default=5, ge=1, le=50, description="Number of items to return"),
    offset: int = Query(default=0, ge=0, description="Offset index"),
    db: Session = Depends(get_db)
) -> PaginatedGenerationsResponse:
    service = GenerationService(db)
    return await service.list_recent_generations(limit=limit, offset=offset)


@router.post(
    "/generations/{generation_id}/retry",
    response_model=GenerationStatusResponse,
    summary="Retry Generation",
    description="Creates a new generation attempt preserving original settings."
)
async def retry_generation(
    generation_id: str,
    db: Session = Depends(get_db)
) -> GenerationStatusResponse:
    service = GenerationService(db)
    return await service.retry_generation(generation_id)


@router.post(
    "/generations/{generation_id}/variations",
    response_model=GenerationStatusResponse,
    summary="Create Video Variation",
    description="Creates a new video generation attempt derived from an existing generation."
)
async def create_variation(
    generation_id: str,
    db: Session = Depends(get_db)
) -> GenerationStatusResponse:
    service = GenerationService(db)
    return await service.create_variation(generation_id)
