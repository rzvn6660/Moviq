import json
import pytest
from unittest.mock import AsyncMock, patch
import httpx

from app.services.director.groq import GroqDirectorProvider
from app.services.director.prompts import DIRECTOR_RESPONSE_SCHEMA
from app.services.director.factory import get_director_provider
from app.core.exceptions import (
    EmptyPromptException,
    PromptTooLongException,
    DirectorConfigurationErrorException,
    DirectorProviderUnavailableException,
    DirectorTimeoutException,
    DirectorRateLimitedException,
    DirectorInvalidResponseException,
)


@pytest.mark.asyncio
async def test_groq_director_success_json_schema():
    provider = GroqDirectorProvider(api_key="gsk_mock_test_key_12345", model="openai/gpt-oss-120b")
    mock_groq_json = {
        "choices": [
            {
                "message": {
                    "content": json.dumps({
                        "enhanced_prompt": "Cinematic macro shot of obsidian perfume bottle on black marble.",
                        "direction": {
                            "subject": "Obsidian perfume bottle",
                            "environment": "Wet black marble",
                            "action": "Smooth 360 rotation",
                            "camera": "Macro 35mm lens",
                            "lighting": "Warm golden volumetric rays",
                            "mood": "Luxurious commercial"
                        },
                        "suggestions": ["Add subtle smoke motes"]
                    })
                }
            }
        ]
    }

    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json = lambda: mock_groq_json

    with patch.object(httpx.AsyncClient, "post", return_value=mock_response) as mock_post:
        res = await provider.enhance_prompt("A perfume bottle on black marble")
        assert res.original_prompt == "A perfume bottle on black marble"
        assert "obsidian perfume bottle" in res.enhanced_prompt.lower()
        assert res.structured_direction.subject == "Obsidian perfume bottle"
        assert res.analysis.score > 0

        # Verify JSON Schema Structured Output request payload
        called_kwargs = mock_post.call_args.kwargs
        json_payload = called_kwargs["json"]
        assert json_payload["model"] == "openai/gpt-oss-120b"
        assert json_payload["response_format"]["type"] == "json_schema"
        assert json_payload["response_format"]["json_schema"]["strict"] is True
        assert json_payload["response_format"]["json_schema"]["name"] == "director_enhancement"


@pytest.mark.asyncio
async def test_groq_director_missing_api_key():
    provider = GroqDirectorProvider(api_key="", fallback_to_mock=False)
    with pytest.raises(DirectorConfigurationErrorException):
        await provider.enhance_prompt("Valid prompt text")


@pytest.mark.asyncio
async def test_groq_director_empty_prompt():
    provider = GroqDirectorProvider(api_key="gsk_mock_test_key")
    with pytest.raises(EmptyPromptException):
        await provider.enhance_prompt("   ")


@pytest.mark.asyncio
async def test_groq_director_overlong_prompt():
    provider = GroqDirectorProvider(api_key="gsk_mock_test_key")
    with pytest.raises(PromptTooLongException):
        await provider.enhance_prompt("A" * 1001)


@pytest.mark.asyncio
async def test_groq_director_rate_limited():
    provider = GroqDirectorProvider(api_key="gsk_mock_test_key", fallback_to_mock=False)
    mock_response = AsyncMock()
    mock_response.status_code = 429

    with patch.object(httpx.AsyncClient, "post", return_value=mock_response):
        with pytest.raises(DirectorRateLimitedException):
            await provider.enhance_prompt("Test prompt")


@pytest.mark.asyncio
async def test_groq_director_timeout():
    provider = GroqDirectorProvider(api_key="gsk_mock_test_key", fallback_to_mock=False)

    with patch.object(httpx.AsyncClient, "post", side_effect=httpx.ReadTimeout("Timeout")):
        with pytest.raises(DirectorTimeoutException):
            await provider.enhance_prompt("Test prompt")


@pytest.mark.asyncio
async def test_groq_director_invalid_json():
    provider = GroqDirectorProvider(api_key="gsk_mock_test_key", fallback_to_mock=False)
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json = lambda: {"choices": [{"message": {"content": "INVALID NON-JSON TEXT"}}]}

    with patch.object(httpx.AsyncClient, "post", return_value=mock_response):
        with pytest.raises(DirectorInvalidResponseException):
            await provider.enhance_prompt("Test prompt")


def test_director_factory_selection():
    from app.core.config import settings
    settings.DIRECTOR_PROVIDER = "mock"
    p_mock = get_director_provider()
    assert "Mock" in p_mock.__class__.__name__

    settings.DIRECTOR_PROVIDER = "groq"
    p_groq = get_director_provider()
    assert "Groq" in p_groq.__class__.__name__

    settings.DIRECTOR_PROVIDER = "mock"
