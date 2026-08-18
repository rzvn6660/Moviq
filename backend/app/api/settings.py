from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional
from app.core.config import settings

router = APIRouter(prefix="/settings", tags=["Execution Mode Settings"])


class ExecutionModeResponse(BaseModel):
    executionMode: str = Field(..., alias="executionMode")
    displayLabel: str = Field(..., alias="displayLabel")
    provider: str = Field(..., alias="provider")
    isSafe: bool = Field(..., alias="isSafe")
    warningMessage: Optional[str] = Field(None, alias="warningMessage")

    model_config = {
        "populate_by_name": True
    }


class UpdateExecutionModeRequest(BaseModel):
    executionMode: str = Field(..., alias="executionMode")

    model_config = {
        "populate_by_name": True
    }


def _get_mode_response(mode_str: str) -> ExecutionModeResponse:
    mode = (mode_str or "safe").lower().strip()
    is_safe = mode == "safe"
    display_label = "SAFE MODE • LOCAL SYNTHETIC" if is_safe else "LIVE MODE • KIE.AI"
    warning = None if is_safe else "Generation requests may consume provider credits."

    return ExecutionModeResponse(
        executionMode=mode,
        displayLabel=display_label,
        provider=settings.VIDEO_PROVIDER,
        isSafe=is_safe,
        warningMessage=warning,
    )


@router.get(
    "/execution-mode",
    response_model=ExecutionModeResponse,
    summary="Get Active Execution Mode",
    description="Returns current application execution mode ('safe' vs 'live') and visual UI badge state."
)
async def get_execution_mode() -> ExecutionModeResponse:
    return _get_mode_response(settings.MOVIQ_EXECUTION_MODE)


@router.put(
    "/execution-mode",
    response_model=ExecutionModeResponse,
    summary="Update Active Execution Mode",
    description="Switches application between SAFE MODE (local synthetic rendering) and LIVE DEMO MODE (Kie.ai paid generation)."
)
async def update_execution_mode(req: UpdateExecutionModeRequest) -> ExecutionModeResponse:
    new_mode = req.executionMode.lower().strip()
    if new_mode not in ("safe", "live"):
        new_mode = "safe"
    settings.MOVIQ_EXECUTION_MODE = new_mode
    return _get_mode_response(new_mode)
