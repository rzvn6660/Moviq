from fastapi import APIRouter
from app.schemas.model_capability import ModelsResponse
from app.services.video.registry import get_all_models

router = APIRouter(tags=["Model Capabilities"])


@router.get(
    "/models",
    response_model=ModelsResponse,
    summary="List Model Capabilities",
    description="Returns backend-owned model capabilities including supported aspect ratios, durations, and negative prompt support."
)
async def list_models() -> ModelsResponse:
    return ModelsResponse(models=get_all_models())
