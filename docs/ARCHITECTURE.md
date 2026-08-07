# Moviq Architecture Overview

Moviq is designed around a **decoupled, provider-independent backend architecture**. 

```
                               ┌──────────────────────────┐
                               │   React 18 + Vite UI     │
                               └────────────┬─────────────┘
                                            │ REST API
                                            ▼
                               ┌──────────────────────────┐
                               │     FastAPI Core API     │
                               └────────────┬─────────────┘
                                            │
               ┌────────────────────────────┼────────────────────────────┐
               ▼                            ▼                            ▼
     ┌──────────────────┐         ┌──────────────────┐         ┌──────────────────┐
     │  AI Director     │         │ Provider Health  │         │ Recommendation   │
     │  Enhancer        │         │ Telemetry Engine │         │ Engine           │
     └──────────────────┘         └──────────────────┘         └──────────────────┘
                                            │
                                            ▼
                               ┌──────────────────────────┐
                               │  BaseVideoProvider Layer │
                               └────────────┬─────────────┘
                                            │
       ┌──────────────┬──────────────┼──────────────┬──────────────┬──────────────┐
       ▼              ▼              ▼              ▼              ▼              ▼
 ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
 │  Kie.ai  │   │ Luma AI  │   │Hailuo AI │   │HuggingFac│   │Remote Wan│   │LTX Video │
 └──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘
```

---

## Key Subsystems

### 1. Unified Provider Lifecycle
Every video provider implements `BaseVideoProvider`:
1. `health_check()`: Diagnostic latency and availability ping.
2. `submit_generation(generation)`: Submits prompt payload and receives job tracking token.
3. `check_status(job_id)`: Async status polling returning percentage and state.
4. `get_result(job_id)`: Returns local H.264 video container URL and metadata.
5. `download_and_store(remote_url)`: Downloads raw provider MP4, validates structure, and stores locally.

### 2. Video Validation Engine v2
All output videos are validated using OpenCV (`cv2`):
- Non-zero file size check.
- Valid MP4 `ftyp` magic header box validation.
- OpenCV `VideoCapture` frame count and FPS inspection.
- Frame perceptual motion calculation (`absdiff` mean threshold check) to reject motionless static frames disguised as MP4s.

### 3. Provider Intelligence Layer
- **Live Health Telemetry**: 45s TTL cached latency and availability monitor.
- **Semantic Recommender Engine**: Rule-based prompt semantics matcher.
- **Truthful Cost Estimator**: Calculates documented credit requirements and runtime.
- **Smart Failover**: Automatic fallback provider sequence with event timeline logging.
