from fastapi import APIRouter
from app.schemas.director import EnhancePromptRequest, EnhancePromptResponse
from app.services.director.factory import get_director_provider

router = APIRouter(tags=["AI Director"])


@router.post(
    "/director/enhance",
    response_model=EnhancePromptResponse,
    summary="Enhance Prompt via AI Director",
    description="Enhances a raw user idea prompt into a structured shot list using configured AI Director (Mock or Groq LLM)."
)
async def enhance_prompt(request: EnhancePromptRequest) -> EnhancePromptResponse:
    provider = get_director_provider()
    return await provider.enhance_prompt(request.prompt)
