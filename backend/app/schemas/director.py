from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class StructuredDirection(BaseModel):
    subject: str
    environment: str
    action: str
    camera: str
    lighting: str
    mood: str

    model_config = ConfigDict(populate_by_name=True)


class PromptAnalysis(BaseModel):
    score: int  # 0 to 100
    label: str  # Basic, Moderate, Detailed, Director Level
    feedback: List[str]

    model_config = ConfigDict(populate_by_name=True)


class EnhancePromptRequest(BaseModel):
    prompt: str


class EnhancePromptResponse(BaseModel):
    original_prompt: str = Field(alias="originalPrompt")
    enhanced_prompt: str = Field(alias="enhancedPrompt")
    structured_direction: StructuredDirection = Field(alias="structuredDirection")
    analysis: PromptAnalysis

    model_config = ConfigDict(populate_by_name=True)
