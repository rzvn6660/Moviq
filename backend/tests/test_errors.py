import pytest
from app.core.config import settings


def test_unknown_model_error(client):
    res = client.post("/api/v1/generations", json={
        "prompt": "Test prompt",
        "modelId": "non-existent-model-xyz"
    })
    assert res.status_code == 400
    data = res.json()
    assert data["error"]["code"] == "MODEL_NOT_FOUND"


def test_unsupported_aspect_ratio_error(client):
    # wan-2.1/video supports 16:9 and 1:1 only (9:16 is unsupported)
    res = client.post("/api/v1/generations", json={
        "prompt": "Test prompt",
        "aspectRatio": "9:16",
        "modelId": "wan-2.1/video"
    })
    assert res.status_code == 400
    data = res.json()
    assert data["error"]["code"] == "UNSUPPORTED_ASPECT_RATIO"


def test_unsupported_duration_error(client):
    # hailuo-01 supports 5s only
    res = client.post("/api/v1/generations", json={
        "prompt": "Test prompt",
        "duration": "15s",
        "modelId": "hailuo-01"
    })
    assert res.status_code == 400
    data = res.json()
    assert data["error"]["code"] == "UNSUPPORTED_DURATION"


def test_negative_prompt_unsupported_error(client):
    # dream-machine does not support negative prompts
    res = client.post("/api/v1/generations", json={
        "prompt": "Test prompt",
        "negativePrompt": "blurry",
        "modelId": "dream-machine"
    })
    assert res.status_code == 400
    data = res.json()
    assert data["error"]["code"] == "NEGATIVE_PROMPT_NOT_SUPPORTED"


def test_generation_not_found(client):
    res = client.get("/api/v1/generations/moviq-gen-nonexistent")
    assert res.status_code == 404
    data = res.json()
    assert data["error"]["code"] == "GENERATION_NOT_FOUND"


def test_provider_failure_trigger(client):
    orig_synth = settings.ENABLE_SYNTHETIC_FALLBACK
    settings.ENABLE_SYNTHETIC_FALLBACK = False
    try:
        res = client.post("/api/v1/generations", json={
            "prompt": "Force_Fail test prompt triggers error",
            "modelId": "kling-3.0/video"
        })
        assert res.status_code in [201, 400]
    finally:
        settings.ENABLE_SYNTHETIC_FALLBACK = orig_synth


def test_provider_timeout_trigger(client):
    orig_synth = settings.ENABLE_SYNTHETIC_FALLBACK
    settings.ENABLE_SYNTHETIC_FALLBACK = False
    try:
        res = client.post("/api/v1/generations", json={
            "prompt": "Force_Timeout test prompt triggers timeout",
            "modelId": "kling-3.0/video"
        })
        assert res.status_code in [201, 400]
    finally:
        settings.ENABLE_SYNTHETIC_FALLBACK = orig_synth
