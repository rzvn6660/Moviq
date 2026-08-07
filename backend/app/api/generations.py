import os
import httpx
import urllib.parse
import ipaddress
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Header, status, HTTPException
from fastapi.responses import StreamingResponse, FileResponse, Response
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.generation import (
    CreateGenerationRequest,
    GenerationStatusResponse,
    PaginatedGenerationsResponse,
    ToggleFavoriteRequest,
    GenerationEventResponse,
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


import re

def generate_human_readable_filename(prompt: Optional[str], gen_id: str) -> str:
    """
    Generates a human-readable, URL-safe slug filename prefixed with moviq- and ending with .mp4.
    Example:
    'A red sports car racing through neon Tokyo.' -> 'moviq-red-sports-car-racing-through-neon-tokyo.mp4'
    'Astronaut walking on Mars.' -> 'moviq-astronaut-walking-on-mars.mp4'
    """
    clean_id = gen_id.replace("moviq-gen-", "").replace("moviq-", "")
    if not prompt or not isinstance(prompt, str) or not prompt.strip():
        return f"moviq-{clean_id}.mp4"

    raw_text = prompt.strip().lower()

    # Strip standalone leading articles ('a ', 'an ', 'the ')
    for art in ["a ", "an ", "the "]:
        if raw_text.startswith(art):
            raw_text = raw_text[len(art):].strip()
            break

    cleaned = re.sub(r"[^\w\s-]", "", raw_text).strip()
    slug = re.sub(r"[\s_]+", "-", cleaned).strip("-")

    if len(slug) > 60:
        slug = slug[:60].rsplit("-", 1)[0]

    if not slug:
        slug = f"video-{clean_id}"

    if not slug.startswith("moviq-"):
        slug = f"moviq-{slug}"

    if not slug.endswith(".mp4"):
        slug = f"{slug}.mp4"

    return slug


@router.get(
    "/generations/{generation_id}/video",
    summary="Serve Video Output File",
    description="Streams the raw generated MP4 file with byte range support for video player scrubbing."
)
async def get_generation_video(
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

    filename = generate_human_readable_filename(gen.original_prompt, gen.id)
    file_size = os.path.getsize(filepath)
    quoted_filename = urllib.parse.quote(filename)

    return FileResponse(
        filepath,
        media_type="video/mp4",
        filename=filename,
        headers={
            "Content-Disposition": f'inline; filename="{filename}"; filename*=UTF-8\'\'{quoted_filename}',
            "Content-Length": str(file_size),
            "Accept-Ranges": "bytes",
            "Cache-Control": "no-cache"
        }
    )


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

    filename = generate_human_readable_filename(gen.original_prompt, gen.id)
    quoted_filename = urllib.parse.quote(filename)

    # Handle local media references (/api/v1/generations/{id}/video)
    if video_url.startswith("/api/v1/"):
        safe_gen_id = os.path.basename(gen.id)
        generated_dir = os.path.abspath(os.path.join(os.getcwd(), "generated"))
        filepath = os.path.abspath(os.path.join(generated_dir, f"moviq_{safe_gen_id}.mp4"))
        if filepath.startswith(generated_dir) and os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            return FileResponse(
                filepath,
                media_type="video/mp4",
                filename=filename,
                headers={
                    "Content-Disposition": f'attachment; filename="{filename}"; filename*=UTF-8\'\'{quoted_filename}',
                    "Content-Length": str(file_size),
                    "Accept-Ranges": "bytes",
                    "Cache-Control": "no-cache"
                }
            )

    # Stream external response chunks asynchronously to avoid loading large files into memory
    async def video_stream_generator():
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                async with client.stream("GET", video_url) as stream_resp:
                    if stream_resp.status_code == 200:
                        async for chunk in stream_resp.aiter_bytes(chunk_size=65536):
                            yield chunk
        except Exception as err:
            logger.warn(f"Streaming error for generation '{generation_id}': {err}")

    return StreamingResponse(
        video_stream_generator(),
        media_type="video/mp4",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"; filename*=UTF-8\'\'{quoted_filename}',
            "Accept-Ranges": "bytes"
        }
    )


@router.get(
    "/generations/{generation_id}/thumbnail",
    summary="Serve Generation Thumbnail",
    description="Serves extracted JPEG thumbnail frame for a video generation."
)
async def get_generation_thumbnail(
    generation_id: str,
    db: Session = Depends(get_db)
):
    gen = db.query(Generation).filter(Generation.id == generation_id).first()
    if not gen:
        raise GenerationNotFoundException(generation_id)

    safe_gen_id = os.path.basename(generation_id)
    generated_dir = os.path.abspath(os.path.join(os.getcwd(), "generated"))
    thumb_path = os.path.abspath(os.path.join(generated_dir, f"thumb_{safe_gen_id}.jpg"))

    if not thumb_path.startswith(generated_dir) or not os.path.exists(thumb_path):
        mp4_path = os.path.abspath(os.path.join(generated_dir, f"moviq_{safe_gen_id}.mp4"))
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
                finally:
                    cap.release()
            except Exception:
                pass

    if os.path.exists(thumb_path):
        return FileResponse(thumb_path, media_type="image/jpeg")

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="640" height="360" viewBox="0 0 640 360">
        <rect width="640" height="360" fill="#0c1324"/>
        <circle cx="320" cy="180" r="48" fill="#151b2d" stroke="#f59e0b" stroke-width="2"/>
        <polygon points="310,160 340,180 310,200" fill="#f59e0b"/>
        <text x="320" y="260" font-family="sans-serif" font-size="14" fill="#94a3b8" text-anchor="middle">MOVIQ AI VIDEO</text>
    </svg>'''
    return Response(content=svg_content, media_type="image/svg+xml")


@router.patch(
    "/generations/{generation_id}/favorite",
    summary="Toggle Generation Favorite",
    description="Toggles the favorite flag on a generation."
)
async def toggle_generation_favorite(
    generation_id: str,
    req: ToggleFavoriteRequest,
    db: Session = Depends(get_db)
):
    service = GenerationService(db)
    return await service.toggle_favorite(generation_id, req.favorite)


@router.delete(
    "/generations/{generation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Generation",
    description="Deletes SQLite database record, MP4 file, and thumbnail file."
)
async def delete_generation(
    generation_id: str,
    db: Session = Depends(get_db)
):
    service = GenerationService(db)
    await service.delete_generation(generation_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


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
    description="Returns generations list with search, filtering, sorting, and pagination."
)
async def list_generations(
    limit: int = Query(default=5, ge=1, le=100, description="Number of items to return"),
    offset: int = Query(default=0, ge=0, description="Offset index"),
    search: Optional[str] = Query(default=None, description="Search term in prompt"),
    status: Optional[str] = Query(default=None, description="Status filter"),
    provider: Optional[str] = Query(default=None, description="Provider filter"),
    model_id: Optional[str] = Query(default=None, alias="modelId", description="Model ID filter"),
    is_favorite: Optional[bool] = Query(default=None, alias="isFavorite", description="Favorites filter"),
    sort_by: Optional[str] = Query(default="newest", alias="sortBy", description="Sorting order"),
    db: Session = Depends(get_db)
) -> PaginatedGenerationsResponse:
    service = GenerationService(db)
    return await service.list_recent_generations(
        limit=limit,
        offset=offset,
        search=search,
        status=status,
        provider=provider,
        model_id=model_id,
        is_favorite=is_favorite,
        sort_by=sort_by
    )


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


@router.get(
    "/generations/{generation_id}/events",
    response_model=List[GenerationEventResponse],
    summary="Get Generation Lifecycle Timeline Events",
    description="Returns full audit timeline of events for a video generation."
)
async def get_generation_events(
    generation_id: str,
    db: Session = Depends(get_db)
) -> List[GenerationEventResponse]:
    service = GenerationService(db)
    return await service.get_generation_events(generation_id)
