# Moviq REST API Documentation

Base URL: `http://localhost:8001/api/v1`

---

## Provider Intelligence Endpoints

### `GET /providers/health`
Returns live telemetry monitoring status for all 6 video provider nodes.

**Query Parameters**:
- `refresh` (boolean, optional): Set `true` to force bypass 45s TTL cache lock.

**Response**:
```json
{
  "providers": [
    {
      "provider": "kie",
      "status": "ONLINE",
      "latency_ms": 120,
      "queue_status": "LOW",
      "configured": true,
      "authenticated": true,
      "available_models": 3,
      "estimated_wait": 5,
      "credits": { "known": false, "remaining": null }
    }
  ],
  "cached_at": "2026-08-07T12:00:00Z"
}
```

### `POST /providers/recommend`
Evaluates prompt semantics and returns optimal provider recommendation.

**Request Body**:
```json
{
  "prompt": "A luxury red sports car drifting through rainy neon Tokyo",
  "priority": "quality"
}
```

**Response**:
```json
{
  "recommended_provider": "kie",
  "recommended_model_id": "kling-3.0/video",
  "confidence": 95,
  "reason": "Automotive / drifting prompt matched Kie Kling 3.0 high-speed motion profile.",
  "fallback_providers": ["hailuo", "luma"]
}
```

---

## Generation Lifecycle Endpoints

### `POST /generations`
Submits a video generation task. Supports optional `Idempotency-Key` header.

**Request Body**:
```json
{
  "prompt": "A perfume bottle rotating on black marble with golden lighting",
  "style": "Cinematic",
  "aspectRatio": "16:9",
  "duration": "5s",
  "modelId": "Wan-AI/Wan2.2-TI2V-5B",
  "smartFailover": false
}
```

### `GET /generations/{id}`
Retrieves generation status, progress percentage, video download URL, and timeline event history.

### `GET /generations/{id}/download`
Streams the verified H.264 MP4 file container with proper `Content-Disposition: attachment; filename="moviq_gen_xxx.mp4"`.
