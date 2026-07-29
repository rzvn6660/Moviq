def test_unknown_model_error(client):
    res = client.post("/api/v1/generations", json={
        "prompt": "Test prompt",
        "modelId": "non-existent-model-xyz"
    })
    assert res.status_code == 400
    data = res.json()
    assert data["error"]["code"] == "MODEL_NOT_FOUND"


def test_unsupported_aspect_ratio_error(client):
    res = client.post("/api/v1/generations", json={
        "prompt": "Test prompt",
        "aspectRatio": "9:16",
        "modelId": "pika-v2.0"  # Pika 2.0 only supports 16:9 and 1:1
    })
    assert res.status_code == 400
    data = res.json()
    assert data["error"]["code"] == "UNSUPPORTED_ASPECT_RATIO"


def test_unsupported_duration_error(client):
    res = client.post("/api/v1/generations", json={
        "prompt": "Test prompt",
        "duration": "15s",
        "modelId": "hunyuan-video-v1"  # Hunyuan only supports 5s and 10s
    })
    assert res.status_code == 400
    data = res.json()
    assert data["error"]["code"] == "UNSUPPORTED_DURATION"


def test_negative_prompt_unsupported_error(client):
    res = client.post("/api/v1/generations", json={
        "prompt": "Test prompt",
        "negativePrompt": "blurry",
        "modelId": "luma-dream-machine"  # Luma does not support negative prompt
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
    res = client.post("/api/v1/generations", json={
        "prompt": "Force_Fail test prompt triggers error",
        "modelId": "hunyuan-video-v1"
    })
    assert res.status_code == 201
    gen_id = res.json()["id"]

    import time
    time.sleep(0.5)

    status_res = client.get(f"/api/v1/generations/{gen_id}")
    assert status_res.status_code == 200
    data = status_res.json()
    assert data["state"] == "FAILED"


def test_provider_timeout_trigger(client):
    res = client.post("/api/v1/generations", json={
        "prompt": "Force_Timeout test prompt triggers timeout",
        "modelId": "hunyuan-video-v1"
    })
    assert res.status_code == 201
    gen_id = res.json()["id"]

    import time
    time.sleep(0.5)

    status_res = client.get(f"/api/v1/generations/{gen_id}")
    assert status_res.status_code == 200
    data = status_res.json()
    assert data["state"] == "TIMED_OUT"
