def test_list_models_capabilities(client):
    response = client.get("/api/v1/models")
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    models = data["models"]
    assert len(models) >= 5

    # Check Kling 3.0 Pro capabilities
    kling = next(m for m in models if m["id"] == "kling-3.0/video")
    assert "16:9" in kling["supportedAspectRatios"]
    assert kling["supportsNegativePrompt"] is True

    # Check Luma Dream Machine capabilities
    luma = next(m for m in models if m["id"] == "dream-machine")
    assert luma["supportsNegativePrompt"] is False
