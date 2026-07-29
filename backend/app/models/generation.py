from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Integer, Float, Text, Enum, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.schemas.common import GenerationStatus, StylePreset, AspectRatio, Duration
import json


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Generation(Base):
    __tablename__ = "generations"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)
    idempotency_key: Mapped[Optional[str]] = mapped_column(String(128), unique=True, index=True, nullable=True)
    parent_generation_id: Mapped[Optional[str]] = mapped_column(String(64), ForeignKey("generations.id"), nullable=True)

    original_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    enhanced_prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    negative_prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    structured_direction_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    style: Mapped[str] = mapped_column(String(32), nullable=False, default="Cinematic")
    aspect_ratio: Mapped[str] = mapped_column(String(16), nullable=False, default="16:9")
    duration: Mapped[str] = mapped_column(String(16), nullable=False, default="5s")

    provider: Mapped[str] = mapped_column(String(32), nullable=False, default="mock")
    model_id: Mapped[str] = mapped_column(String(64), nullable=False, default="hunyuan-video-v1")
    provider_job_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)

    status: Mapped[GenerationStatus] = mapped_column(
        Enum(GenerationStatus),
        nullable=False,
        default=GenerationStatus.QUEUED,
        index=True
    )
    progress_percentage: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=0)

    video_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    generation_time_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    error_code: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)

    def set_structured_direction(self, direction_dict: dict):
        self.structured_direction_json = json.dumps(direction_dict)

    def get_structured_direction(self) -> dict:
        if self.structured_direction_json:
            try:
                return json.loads(self.structured_direction_json)
            except Exception:
                pass
        return {}
