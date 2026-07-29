def test_enhance_prompt_success(client):
    payload = {"prompt": "A luxury perfume bottle rotating on black marble with warm golden lighting."}
    response = client.post("/api/v1/director/enhance", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["originalPrompt"] == payload["prompt"]
    assert len(data["enhancedPrompt"]) > 20
    assert data["structuredDirection"]["subject"] is not None
    assert data["structuredDirection"]["lighting"] is not None
    assert data["analysis"]["score"] > 50


def test_enhance_prompt_empty_rejection(client):
    payload = {"prompt": "   "}
    response = client.post("/api/v1/director/enhance", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert data["error"]["code"] == "EMPTY_PROMPT"
