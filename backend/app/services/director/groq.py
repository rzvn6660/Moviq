import json
import httpx
from typing import Optional
from app.services.director.base import DirectorProvider
from app.services.director.prompts import DIRECTOR_SYSTEM_PROMPT, DIRECTOR_RESPONSE_SCHEMA
from app.services.director.scorer import PromptScorer
from app.services.director.cache import DirectorEnhancementCache
from app.schemas.director import EnhancePromptResponse, StructuredDirection, PromptAnalysis
from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import (
    EmptyPromptException,
    PromptTooLongException,
    DirectorConfigurationErrorException,
    DirectorProviderUnavailableException,
    DirectorTimeoutException,
    DirectorRateLimitedException,
    DirectorInvalidResponseException,
)


class GroqDirectorProvider(DirectorProvider):
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout_seconds: float = 15.0,
        fallback_to_mock: Optional[bool] = None,
    ):
        self.api_key = api_key if api_key is not None else settings.GROQ_API_KEY
        self.model = model or settings.GROQ_MODEL
        self.timeout_seconds = timeout_seconds
        self.fallback_to_mock = fallback_to_mock if fallback_to_mock is not None else settings.DIRECTOR_FALLBACK_TO_MOCK
        self.cache = DirectorEnhancementCache()

    def _get_response_format(self) -> dict:
        """
        Returns JSON Schema structured output format for models supporting strict mode (e.g. openai/gpt-oss-120b),
        falling back to json_object for legacy models.
        """
        # Models supporting strict JSON Schema structured output
        schema_supported_models = ["openai/gpt-oss-120b", "llama-3.3-70b-versatile"]
        if any(m in self.model.lower() for m in ["gpt-oss", "json_schema"]) or self.model in schema_supported_models:
            return {
                "type": "json_schema",
                "json_schema": DIRECTOR_RESPONSE_SCHEMA
            }
        return {"type": "json_object"}

    async def enhance_prompt(self, prompt: str) -> EnhancePromptResponse:
        trimmed = prompt.strip()
        if not trimmed:
            raise EmptyPromptException()
        if len(trimmed) > 1000:
            raise PromptTooLongException(1000)

        # Check cache
        cached_res = self.cache.get(trimmed)
        if cached_res:
            logger.info(f"Returning cached Groq AI Director enhancement for prompt length {len(trimmed)}")
            return cached_res

        # Check API key configuration
        if not self.api_key:
            logger.error("GROQ_API_KEY is not configured in backend settings")
            if self.fallback_to_mock:
                from app.services.director.mock import MockDirectorProvider
                logger.warn("DIRECTOR_FALLBACK_TO_MOCK is True. Falling back to MockDirectorProvider")
                return await MockDirectorProvider().enhance_prompt(trimmed)
            raise DirectorConfigurationErrorException("GROQ_API_KEY is not configured on the backend server")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": DIRECTOR_SYSTEM_PROMPT},
                {"role": "user", "content": f"Idea prompt to direct: {trimmed}"},
            ],
            "temperature": 0.5,
            "response_format": self._get_response_format(),
        }

        logger.info(f"Dispatching AI Director prompt enhancement to Groq ({self.model}), prompt length: {len(trimmed)}")

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers=headers,
                    json=payload,
                )

            if response.status_code == 429:
                logger.warn("Groq API rate limit exceeded (429)")
                raise DirectorRateLimitedException()
            elif response.status_code in (401, 403):
                logger.error(f"Groq API authentication error ({response.status_code})")
                raise DirectorConfigurationErrorException("Groq API authentication failed. Check GROQ_API_KEY.")
            elif response.status_code >= 500:
                logger.error(f"Groq API server error ({response.status_code})")
                raise DirectorProviderUnavailableException(f"Groq service error code {response.status_code}")
            elif response.status_code != 200:
                logger.error(f"Groq API error status {response.status_code}: {response.text[:200]}")
                raise DirectorProviderUnavailableException(f"Groq returned HTTP {response.status_code}")

            res_json = response.json()
            content_str = res_json["choices"][0]["message"]["content"]
            parsed = json.loads(content_str)

        except (httpx.TimeoutException, httpx.ConnectTimeout, httpx.ReadTimeout) as err:
            logger.warn(f"Groq API request timed out: {err}")
            if self.fallback_to_mock:
                from app.services.director.mock import MockDirectorProvider
                return await MockDirectorProvider().enhance_prompt(trimmed)
            raise DirectorTimeoutException()

        except httpx.RequestError as err:
            logger.error(f"Groq API network request failed: {err}")
            if self.fallback_to_mock:
                from app.services.director.mock import MockDirectorProvider
                return await MockDirectorProvider().enhance_prompt(trimmed)
            raise DirectorProviderUnavailableException()

        except (json.JSONDecodeError, KeyError) as err:
            logger.error(f"Failed to parse structured JSON response from Groq: {err}")
            raise DirectorInvalidResponseException()

        # Extract & validate structured content via Pydantic
        try:
            enhanced_prompt = parsed.get("enhanced_prompt", trimmed)
            dir_data = parsed.get("direction", {})
            suggestions = parsed.get("suggestions", [])

            structured_direction = StructuredDirection(
                subject=dir_data.get("subject", trimmed),
                environment=dir_data.get("environment", "Cinematic environment"),
                action=dir_data.get("action", "Dynamic camera motion"),
                camera=dir_data.get("camera", "35mm anamorphic prime lens"),
                lighting=dir_data.get("lighting", "Volumetric lighting"),
                mood=dir_data.get("mood", "Cinematic")
            )
        except Exception as err:
            logger.error(f"Validation error mapping Groq JSON: {err}")
            raise DirectorInvalidResponseException("Groq structured JSON did not match expected schema")

        # Evaluate deterministic score before and after
        score_before, _, _ = PromptScorer.evaluate(trimmed)
        score_after, label_after, feedback_after = PromptScorer.evaluate(enhanced_prompt)

        all_feedback = suggestions if suggestions else feedback_after

        result = EnhancePromptResponse(
            original_prompt=trimmed,
            enhanced_prompt=enhanced_prompt,
            structured_direction=structured_direction,
            analysis=PromptAnalysis(
                score=score_after,
                label=label_after,
                feedback=all_feedback
            )
        )

        # Cache valid response
        self.cache.set(trimmed, result)
        return result
