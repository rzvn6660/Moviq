from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.core.exceptions import MoviqException
from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.api.router import api_router
from app.models.generation import Generation
from app.schemas.common import GenerationStatus
from datetime import datetime, timezone
import json


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup logging & Database tables
    setup_logging()
    logger.info("Initializing Moviq database tables...")
    Base.metadata.create_all(bind=engine)

    # Seed mock history if database is empty
    db = SessionLocal()
    try:
        count = db.query(Generation).count()
        if count == 0:
            logger.info("Seeding initial mock generations into database...")
            mock_seed = [
                Generation(
                    id="moviq-gen-8812",
                    original_prompt="A luxury perfume bottle rotating on black marble with warm golden lighting.",
                    enhanced_prompt="Cinematic commercial macro shot of a sleek obsidian perfume bottle with embossed gold typography, spinning smoothly on wet black marble. Volumetric warm tungsten spotlighting casts sharp golden caustics and subtle dust particles hovering in the atmosphere. 35mm film grain, anamorphic lens flare, 60fps slow motion.",
                    negative_prompt="blurry, oversaturated, low quality, jittery motion",
                    structured_direction_json=json.dumps({
                        "subject": "Obsidian perfume bottle with gold embossed branding",
                        "environment": "Wet black polished marble reflecting warm light reflections",
                        "action": "Smooth 360-degree rotation with subtle floating dust particles",
                        "camera": "Low-angle macro 35mm anamorphic tracking camera",
                        "lighting": "Warm 3200K volumetric spot with high caustics contrast",
                        "mood": "Sophisticated, luxurious, high-fashion commercial"
                    }),
                    style="Cinematic",
                    aspect_ratio="16:9",
                    duration="5s",
                    provider="fal-ai",
                    model_id="hunyuan-video-v1",
                    status=GenerationStatus.COMPLETED,
                    progress_percentage=100,
                    video_url="https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
                    thumbnail_url="https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?auto=format&fit=crop&w=1200&q=80",
                    generation_time_seconds=8.4,
                    created_at=datetime.now(timezone.utc)
                ),
                Generation(
                    id="moviq-gen-8811",
                    original_prompt="Cyberpunk futuristic supercar speeding through Tokyo neon rain at night.",
                    enhanced_prompt="High-speed tracking shot of a matte-black futuristic hypercar with glowing cyan neon underglow, drifting through wet Tokyo streets under towering holographic billboards. Dynamic rain droplets streaking across anamorphic camera lens, reflection on asphalt puddles, atmospheric fog.",
                    structured_direction_json=json.dumps({
                        "subject": "Matte-black aerodynamic hypercar with cyan LED accents",
                        "environment": "Dystopian Tokyo alleyways wet with rain and vibrant neon reflections",
                        "action": "High-speed drift carving around a corner at high velocity",
                        "camera": "Pursuit drone tracking camera with dynamic tilt and motion blur",
                        "lighting": "High contrast cyan and magenta neon signage backlight",
                        "mood": "Exhilarating, dark cyberpunk, cinematic adrenaline"
                    }),
                    style="Realistic",
                    aspect_ratio="16:9",
                    duration="10s",
                    provider="luma-ai",
                    model_id="luma-dream-machine",
                    status=GenerationStatus.COMPLETED,
                    progress_percentage=100,
                    video_url="https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4",
                    thumbnail_url="https://images.unsplash.com/photo-1508974239320-0a029497e820?auto=format&fit=crop&w=1200&q=80",
                    generation_time_seconds=14.2,
                    created_at=datetime.now(timezone.utc)
                )
            ]
            db.add_all(mock_seed)
            db.commit()
    finally:
        db.close()

    yield
    logger.info("Shutting down Moviq backend engine...")


app = FastAPI(
    title="Moviq AI Video Studio API",
    description="Backend API for Moviq AI Video Studio — Turn Ideas Into Motion.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception Handlers
@app.exception_handler(MoviqException)
async def moviq_exception_handler(request: Request, exc: MoviqException):
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail,
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An internal server error occurred.",
                "retryable": True
            }
        },
    )

# Include Router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)
