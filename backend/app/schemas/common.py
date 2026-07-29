from enum import Enum
from typing import Optional, Any, Dict
from pydantic import BaseModel


class GenerationStatus(str, Enum):
    QUEUED = "QUEUED"
    ENHANCING = "ENHANCING"
    SUBMITTED = "SUBMITTED"
    GENERATING = "GENERATING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    TIMED_OUT = "TIMED_OUT"


class StylePreset(str, Enum):
    CINEMATIC = "Cinematic"
    REALISTIC = "Realistic"
    ANIME = "Anime"
    THREE_D = "3D"


class AspectRatio(str, Enum):
    SIXTEEN_NINE = "16:9"
    NINE_SIXTEEN = "9:16"
    ONE_ONE = "1:1"


class Duration(str, Enum):
    FIVE_S = "5s"
    TEN_S = "10s"
    FIFTEEN_S = "15s"


class ErrorDetail(BaseModel):
    code: str
    message: str
    retryable: bool = False
    details: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    error: ErrorDetail
