def test_recent_history_default_five(client):
    # Create 7 generations
    for i in range(7):
        client.post("/api/v1/generations", json={
            "prompt": f"Generation prompt test item #{i}",
            "style": "Cinematic",
            "aspectRatio": "16:9",
            "duration": "5s",
            "modelId": "hunyuan-video-v1"
        })

    # Default query (no limit parameter passed)
    res = client.get("/api/v1/generations")
    assert res.status_code == 200
    data = res.json()
    assert data["limit"] == 5
    assert len(data["generations"]) == 5
    assert data["totalCount"] >= 7

    # Check newest first order
    newest_prompt = data["generations"][0]["originalPrompt"]
    assert "#6" in newest_prompt or "Generation" in newest_prompt
