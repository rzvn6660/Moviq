import uuid
import json
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy import select, func, desc
from sqlalchemy.orm import Session
from app.models.generation import Generation, GenerationEvent
from app.schemas.common import GenerationStatus


class GenerationsRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, generation: Generation) -> Generation:
        self.db.add(generation)
        self.db.commit()
        self.db.refresh(generation)
        return generation

    def get_by_id(self, generation_id: str) -> Optional[Generation]:
        return self.db.query(Generation).filter(Generation.id == generation_id).first()

    def get_by_idempotency_key(self, idempotency_key: str) -> Optional[Generation]:
        if not idempotency_key:
            return None
        return self.db.query(Generation).filter(Generation.idempotency_key == idempotency_key).first()

    def list_recent(self, limit: int = 5, offset: int = 0) -> Tuple[List[Generation], int]:
        return self.list_filtered(limit=limit, offset=offset)

    def list_filtered(
        self,
        limit: int = 20,
        offset: int = 0,
        search: Optional[str] = None,
        status: Optional[str] = None,
        provider: Optional[str] = None,
        model_id: Optional[str] = None,
        is_favorite: Optional[bool] = None,
        sort_by: Optional[str] = "newest"
    ) -> Tuple[List[Generation], int]:
        query = self.db.query(Generation)

        if search and search.strip():
            term = f"%{search.strip().lower()}%"
            query = query.filter(
                func.lower(Generation.original_prompt).like(term) |
                func.lower(Generation.enhanced_prompt).like(term)
            )

        if status and status.strip():
            status_str = status.strip().upper()
            if status_str in GenerationStatus.__members__:
                query = query.filter(Generation.status == GenerationStatus[status_str])

        if provider and provider.strip():
            query = query.filter(func.lower(Generation.provider) == provider.strip().lower())

        if model_id and model_id.strip():
            query = query.filter(func.lower(Generation.model_id) == model_id.strip().lower())

        if is_favorite is not None:
            query = query.filter(Generation.is_favorite == is_favorite)

        total_count = query.count()

        if sort_by == "oldest":
            query = query.order_by(Generation.created_at.asc())
        elif sort_by == "alphabetical":
            query = query.order_by(Generation.original_prompt.asc())
        elif sort_by == "favorite_date":
            query = query.order_by(desc(Generation.favorite_at), desc(Generation.created_at))
        else:  # newest / default
            query = query.order_by(desc(Generation.created_at))

        items = query.offset(offset).limit(limit).all()
        return items, total_count

    def toggle_favorite(self, generation_id: str, favorite: bool) -> Optional[Generation]:
        gen = self.get_by_id(generation_id)
        if not gen:
            return None
        gen.is_favorite = favorite
        gen.favorite_at = datetime.now(timezone.utc) if favorite else None
        self.db.commit()
        self.db.refresh(gen)
        return gen

    def delete(self, generation_id: str) -> bool:
        gen = self.get_by_id(generation_id)
        if not gen:
            return False

        # Clear parent reference from child rows to avoid FK constraint errors
        self.db.query(Generation).filter(Generation.parent_generation_id == generation_id).update(
            {Generation.parent_generation_id: None}, synchronize_session=False
        )

        self.db.delete(gen)
        self.db.commit()
        return True

    def update_status(
        self,
        generation_id: str,
        status: GenerationStatus,
        progress_percentage: Optional[int] = None
    ) -> Optional[Generation]:
        gen = self.get_by_id(generation_id)
        if not gen:
            return None
        gen.status = status
        if progress_percentage is not None:
            gen.progress_percentage = progress_percentage
        self.db.commit()
        self.db.refresh(gen)
        return gen

    def update_result(
        self,
        generation_id: str,
        video_url: str,
        thumbnail_url: str,
        generation_time_seconds: float
    ) -> Optional[Generation]:
        gen = self.get_by_id(generation_id)
        if not gen:
            return None
        gen.status = GenerationStatus.COMPLETED
        gen.video_url = video_url
        gen.thumbnail_url = thumbnail_url
        gen.generation_time_seconds = generation_time_seconds
        gen.progress_percentage = 100
        self.db.commit()
        self.db.refresh(gen)
        return gen

    def update_error(
        self,
        generation_id: str,
        error_code: str,
        error_message: str,
        status: GenerationStatus = GenerationStatus.FAILED
    ) -> Optional[Generation]:
        gen = self.get_by_id(generation_id)
        if not gen:
            return None
        gen.status = status
        gen.error_code = error_code
        gen.error_message = error_message
        self.db.commit()
        self.db.refresh(gen)
        return gen

    def log_event(
        self,
        generation_id: str,
        step: str,
        status: str = "SUCCESS",
        started_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None,
        duration_ms: Optional[int] = 0,
        details: Optional[dict] = None
    ) -> GenerationEvent:
        now = datetime.now(timezone.utc)
        start = started_at or now
        comp = completed_at or now
        dur = duration_ms if duration_ms is not None else int((comp - start).total_seconds() * 1000)

        evt = GenerationEvent(
            id=f"evt-{uuid.uuid4().hex[:12]}",
            generation_id=generation_id,
            step=step,
            status=status,
            started_at=start,
            completed_at=comp,
            duration_ms=max(0, dur),
            details_json=json.dumps(details) if details else None
        )
        self.db.add(evt)
        self.db.commit()
        self.db.refresh(evt)
        return evt

    def get_events(self, generation_id: str) -> List[GenerationEvent]:
        return self.db.query(GenerationEvent).filter(
            GenerationEvent.generation_id == generation_id
        ).order_by(GenerationEvent.started_at.asc()).all()
