from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Integer, Float, Text, Enum, DateTime, ForeignKey, Boolean
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
    model_id: Mapped[str] = mapped_column(String(64), nullable=False, default="Wan-AI/Wan2.2-TI2V-5B")
    execution_mode: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, default="Hosted Inference")
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
    is_synthetic: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_favorite: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    favorite_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    fidelity_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=0.92)
    fidelity_label: Mapped[Optional[str]] = mapped_column(String(32), nullable=True, default="High Fidelity")

    smart_failover: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    cost_estimate_credits: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=0.0)
    failover_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

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


class GenerationEvent(Base):
    __tablename__ = "generation_events"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)
    generation_id: Mapped[str] = mapped_column(String(64), ForeignKey("generations.id", ondelete="CASCADE"), index=True, nullable=False)
    step: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="SUCCESS")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=0)
    details_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def set_details(self, details_dict: dict):
        self.details_json = json.dumps(details_dict) if details_dict else None

    def get_details(self) -> dict:
        if not self.details_json:
            return {}
        try:
            return json.loads(self.details_json)
        except Exception:
            return {}


class ProviderMetric(Base):
    __tablename__ = "provider_metrics"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)
    provider: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    model_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    event_type: Mapped[str] = mapped_column(String(32), nullable=False, default="GENERATION") # HEALTH_CHECK, GENERATION, FAILOVER, DOWNLOAD
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="SUCCESS")
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    queue_delay_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=0)
    validation_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=0)
    file_size_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=0)
    error_code: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now, index=True)

