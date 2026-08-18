from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    DATABASE_URL: str = "sqlite:///./moviq.db"
    CORS_ORIGINS: List[str] = [
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    MOVIQ_EXECUTION_MODE: str = "safe"  # "safe" (local synthetic rendering) or "live" (explicit user-triggered paid generation)
    VIDEO_PROVIDER: str = "kie"  # "kie", "luma", "hailuo", "huggingface", "remote_wan", "ltx", or "mock"
    KIE_API_KEY: Optional[str] = None
    KIE_BASE_URL: str = "https://api.kie.ai"
    KIE_MODEL: str = "kling-3.0/video"

    LUMA_API_KEY: Optional[str] = None
    HAILUO_API_KEY: Optional[str] = None

    HF_TOKEN: Optional[str] = None
    HF_VIDEO_MODEL: str = "Wan-AI/Wan2.2-TI2V-5B"
    HF_INFERENCE_PROVIDER: Optional[str] = "fal-ai"

    REMOTE_WAN_URL: Optional[str] = "http://localhost:8002"
    REMOTE_WAN_API_KEY: Optional[str] = None
    REMOTE_WAN_TIMEOUT_SECONDS: int = 900
    WAN_NUM_INFERENCE_STEPS: int = 20
    WAN_GUIDANCE_SCALE: float = 5.0
    WAN_FPS: int = 16

    DIRECTOR_PROVIDER: str = "mock"  # "mock" or "groq"
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "openai/gpt-oss-120b"
    DIRECTOR_FALLBACK_TO_MOCK: bool = False
    GENERATION_TIMEOUT_SECONDS: int = 600
    ENABLE_SYNTHETIC_FALLBACK: bool = False
    HEALTH_CACHE_TTL_SECONDS: int = 45
    POLL_INTERVAL_SECONDS: float = 2.0
    POLL_MAX_ATTEMPTS: int = 300
    STORAGE_DIR: str = "generated"
    THUMBNAIL_WIDTH: int = 320
    THUMBNAIL_HEIGHT: int = 180

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
