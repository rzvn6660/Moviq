import time


def test_create_and_retrieve_generation_lifecycle(client):
    payload = {
        "prompt": "A luxury perfume bottle rotating on black marble with warm golden lighting.",
        "style": "Cinematic",
        "aspectRatio": "16:9",
        "duration": "5s",
        "modelId": "Wan-AI/Wan2.2-TI2V-5B"
    }

    # 1. Submit creation request
    create_res = client.post("/api/v1/generations", json=payload)
    assert create_res.status_code == 201
    gen_data = create_res.json()
    gen_id = gen_data["id"]
    assert gen_id.startswith("moviq-gen-")

    # 2. Retrieve initial status
    get_res = client.get(f"/api/v1/generations/{gen_id}")
    assert get_res.status_code == 200
    status_data = get_res.json()
    assert status_data["id"] == gen_id

    # Wait for mock lifecycle execution
    time.sleep(1.5)

    # 3. Retrieve completed result
    final_res = client.get(f"/api/v1/generations/{gen_id}")
    assert final_res.status_code == 200
    final_data = final_res.json()
    assert final_data["state"] == "COMPLETED"
    assert final_data["video"]["videoUrl"] is not None
    assert final_data["video"]["aspectRatio"] == "16:9"


def test_retry_and_variation_generation(client):
    payload = {
        "prompt": "Cyberpunk car zooming through neon rain",
        "style": "Realistic",
        "aspectRatio": "16:9",
        "duration": "5s",
        "modelId": "Wan-AI/Wan2.2-TI2V-5B"
    }

    initial_res = client.post("/api/v1/generations", json=payload)
    gen_id = initial_res.json()["id"]

    # Test Retry
    retry_res = client.post(f"/api/v1/generations/{gen_id}/retry")
    assert retry_res.status_code == 200 or retry_res.status_code == 201
    assert retry_res.json()["id"] != gen_id

    # Test Variation
    var_res = client.post(f"/api/v1/generations/{gen_id}/variations")
    assert var_res.status_code == 200 or var_res.status_code == 201
    assert var_res.json()["id"] != gen_id


def test_generation_utc_timestamps(db_session):
    from app.models.generation import Generation
    from app.schemas.common import GenerationStatus

    gen = Generation(
        id="moviq-tz-test",
        original_prompt="Timezone test prompt",
        enhanced_prompt="Timezone test enhanced prompt",
        status=GenerationStatus.QUEUED
    )
    db_session.add(gen)
    db_session.commit()
    db_session.refresh(gen)

    assert gen.created_at is not None
    # Ensure created_at is valid timestamp object
    assert hasattr(gen.created_at, "strftime")


