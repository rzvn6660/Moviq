from typing import List, Optional, Tuple
from sqlalchemy import select, func, desc
from sqlalchemy.orm import Session
from app.models.generation import Generation
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
        total_count = self.db.query(func.count(Generation.id)).scalar() or 0
        generations = (
            self.db.query(Generation)
            .order_by(desc(Generation.created_at))
            .offset(offset)
            .limit(limit)
            .all()
        )
        return generations, total_count

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
