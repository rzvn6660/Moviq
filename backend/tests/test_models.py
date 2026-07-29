def test_list_models_capabilities(client):
    response = client.get("/api/v1/models")
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    models = data["models"]
    assert len(models) >= 4

    # Check Hunyuan Video capabilities
    hunyuan = next(m for m in models if m["id"] == "hunyuan-video-v1")
    assert "16:9" in hunyuan["supportedAspectRatios"]
    assert hunyuan["supportsNegativePrompt"] is True

    # Check Luma capabilities
    luma = next(m for m in models if m["id"] == "luma-dream-machine")
    assert luma["supportsNegativePrompt"] is False
