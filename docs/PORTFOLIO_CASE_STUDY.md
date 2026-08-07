# Portfolio Case Study: Moviq — Modular AI Video Generation Studio

---

## 1. Executive Summary & Problem
AI video generation models are proliferating rapidly across cloud APIs (Kie.ai, Luma, MiniMax Hailuo, Hugging Face) and open-source local PyTorch weights (Wan 2.2, LTX Video). However, developers face significant challenges:
- **API Fragmentation**: Different REST endpoints, polling schemes, payload formats, and credit systems.
- **Silent Degradation**: Upstream providers occasionally return static images disguised as MP4s or time out silently.
- **Observability Gap**: Users lack microsecond timeline visibility into latent space rendering, queue delay, and download validation.

**Moviq** was built to solve these challenges by creating a decoupled, provider-independent video generation backplane.

---

## 2. Architecture & Design Decisions

### Factory Pattern & Provider Abstraction
All video providers inherit from `BaseVideoProvider` and implement an identical 10-step lifecycle contract (`health_check`, `submit_generation`, `check_status`, `get_result`, `download_and_store`, `validate`, `cleanup`). The provider factory (`app/services/video/factory.py`) routes model requests dynamically based on declarative registry definitions.

### Computer Vision Frame Motion Validation (v2)
Rather than trusting upstream HTTP `200 OK` status codes, Moviq passes every downloaded MP4 to an OpenCV inspection pipeline (`app/utils/video_validator.py`):
1. Validates MP4 `ftyp` box header bytes.
2. Reads frame stream via `cv2.VideoCapture`.
3. Computes perceptual motion difference (`absdiff`) between initial and midpoint frames (`gray0`, `gray_mid`).
4. Rejects static images disguised as MP4s with `INVALID_VIDEO` error code.

### Provider Telemetry & Smart Failover
- **Health Telemetry**: Monitors latency, queue traffic, and credentials with an async 45-second TTL cache lock.
- **Smart Failover**: If primary submission fails, Moviq transparently attempts the secondary provider in sequence, logging every attempt to the `GenerationEvent` audit timeline.

---

## 3. Measurable Results & Quality Engineering
- **100% Test Pass Rate**: 87 automated unit, integration, and stress tests passing in Pytest (12.87s execution time).
- **Zero Build Errors**: Vite production bundle and strict TypeScript compilation (`tsc -b`) transform 1804 modules cleanly.
- **Zero Resource Leaks**: All OpenCV `VideoCapture` and `VideoWriter` instances utilize `try/finally` cleanup blocks.
