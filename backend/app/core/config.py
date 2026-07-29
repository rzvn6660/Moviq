from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    DATABASE_URL: str = "sqlite:///./moviq.db"
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    VIDEO_PROVIDER: str = "mock"  # "mock", "fal", "huggingface", or "wan"
    FAL_KEY: Optional[str] = None
    FAL_MODEL: str = "fal-ai/kling-video/v2.5-turbo/pro/text-to-video"

    HF_TOKEN: Optional[str] = None
    HF_VIDEO_MODEL: str = "Lightricks/LTX-Video"
    HF_INFERENCE_PROVIDER: Optional[str] = None

    WAN_MODEL_ID: str = "Wan-AI/Wan2.1-T2V-1.3B-Diffusers"
    WAN_DEVICE: str = "cuda"
    WAN_DTYPE: str = "float16"
    WAN_NUM_INFERENCE_STEPS: int = 20
    WAN_GUIDANCE_SCALE: float = 5.0
    WAN_FPS: int = 16

    DIRECTOR_PROVIDER: str = "mock"  # "mock" or "groq"
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "openai/gpt-oss-120b"
    DIRECTOR_FALLBACK_TO_MOCK: bool = False
    GENERATION_TIMEOUT_SECONDS: int = 600

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
