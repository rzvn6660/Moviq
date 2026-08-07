# Moviq — Technical Interview Question & Answer Guide

> A comprehensive guide covering the top 50 technical interview questions, design decisions, architectural trade-offs, security controls, computer vision pipelines, and concurrency strategies implemented in Moviq.

---

## Section 1: Architecture & Provider Abstraction

### Q1: How does Moviq abstract different AI video providers behind a single backend?
**Answer**: Moviq uses the **Factory Pattern** and **Polymorphism**. All video provider classes (e.g., `KieVideoProvider`, `LumaVideoProvider`, `HailuoVideoProvider`, `HuggingFaceVideoProvider`, `RemoteWanVideoProvider`, `LtxVideoProvider`) inherit from abstract base class `BaseVideoProvider` (`app/services/video/base.py`). Every provider implements an identical lifecycle contract (`health_check`, `submit_generation`, `check_status`, `get_result`, `download_and_store`). The factory (`app/services/video/factory.py`) dynamically instantiates the appropriate provider based on declarative model registry metadata in `registry.py`.

### Q2: Why did you choose FastAPI over Flask or Django for the backend?
**Answer**: FastAPI provides native **asyncio support**, high-throughput asynchronous execution, and automatic OpenAPI schema generation with Pydantic v2. Since video generation involves asynchronous I/O (polling provider REST APIs, streaming binary MP4 containers, background task execution), FastAPI's async/await capabilities prevent thread pool starvation.

### Q3: How do you handle idempotency during generation submission?
**Answer**: Clients pass a unique `Idempotency-Key` header with generation requests. In `GenerationService.create_generation()`, Moviq checks SQLite for an existing record with that key before initiating a job. If a matching key exists, it immediately returns the existing status object, preventing duplicate worker jobs or double-billing upstream providers.

### Q4: How is provider capability data structured and delivered to the frontend?
**Answer**: Provider capabilities (supported aspect ratios, max duration, negative prompt support, execution mode) are declared centrally in `backend/app/services/video/registry.py`. The `GET /api/v1/models` endpoint exposes this registry. The React frontend dynamically renders model picker cards and configures input validation rules directly from this payload, eliminating duplicated UI configuration.

### Q5: What design pattern is used for the AI Director prompt enhancer?
**Answer**: The AI Director uses the **Strategy Pattern**. It defines `BaseDirectorProvider` with concrete implementations `GroqDirectorProvider` (using Groq LLM) and `MockDirectorProvider`. If Groq API rate limits or network errors occur, Moviq seamlessly falls back to the structured rule-based enhancer without throwing runtime exceptions.

---

## Section 2: Computer Vision & Video Processing

### Q6: How does Moviq validate that a generated MP4 file is not corrupted or static?
**Answer**: Moviq implements a 4-step computer vision inspection pipeline in `backend/app/utils/video_validator.py`:
1. Checks file existence and non-zero byte size.
2. Validates MP4 `ftyp` box header bytes (`len(header) >= 8` and `b"ftyp" in header`).
3. Reads video stream via OpenCV `cv2.VideoCapture`, verifying `fps > 0` and `frame_count > 1`.
4. Reads frame 0 (`frame0`) and midpoint frame (`frame_mid`), converts to grayscale, and computes perceptual motion difference via `cv2.absdiff(gray0, gray_mid)`. If `mean_diff < 0.0001`, the video is rejected with `INVALID_VIDEO` status code.

### Q7: How do you prevent OpenCV memory leaks when processing video streams?
**Answer**: All OpenCV `VideoCapture` and `VideoWriter` calls in `video_validator.py` are wrapped in `try/finally` blocks ensuring `cap.release()` and `out.release()` are executed even if exceptions occur during frame processing.

### Q8: How does synthetic fallback video generation work during offline development or testing?
**Answer**: In `generate_synthetic_mp4()`, Moviq uses OpenCV `VideoWriter` to render a 5-second 24fps MP4 video locally. It computes a color seed from the prompt hash, renders animated color gradients, embeds prompt text overlays and timestamp text, and writes valid MP4 frames to disk. This gives developers a full end-to-end visual workflow without requiring active paid API keys.

---

## Section 3: Telemetry, Benchmarking & Failover

### Q9: How does the Provider Health Telemetry Service avoid overloading upstream APIs?
**Answer**: `ProviderHealthService` implements an asynchronous **45-second TTL cache lock** using `asyncio.Lock()`. Subsequent health requests within 45 seconds return cached telemetry data unless `refresh=true` is explicitly passed.

### Q10: How does Smart Failover work when a provider fails?
**Answer**: Smart Failover is disabled by default (`smart_failover: false`). When enabled in `AdvancedSettings.tsx`, if the primary provider submission fails (e.g., HTTP 503 or quota limit), `GenerationService` catches the exception, logs a `Smart Failover Triggered` warning to the `GenerationEvent` timeline, and attempts the secondary compatible provider in sequence.

### Q11: How are provider performance benchmarks calculated?
**Answer**: Benchmarks are computed empirically by aggregating `ProviderMetric` database records. Moviq calculates average generation time, queue delay, success rate percentage, and motion scores from recorded generation telemetry.

---

## Section 4: Security & DevOps

### Q12: How does Moviq protect provider API credentials?
**Answer**: All provider credentials (`KIE_API_KEY`, `HF_TOKEN`, `LUMA_API_KEY`, `HAILUO_API_KEY`) remain strictly backend-only inside `backend/.env`. They are loaded via Pydantic `BaseSettings` (`app/core/config.py`) and are never exposed in REST responses or frontend JavaScript bundles.

### Q13: How does Moviq mitigate SSRF (Server-Side Request Forgery) attacks during video downloads?
**Answer**: In `app/api/generations.py`, remote video URLs pass through `is_safe_download_url()`, which validates that destination domain IPs do not point to loopback interfaces (`127.0.0.1`, `localhost`), private subnets (`10.0.0.0/8`, `192.168.0.0/16`), or non-HTTP schemes (`file://`, `ftp://`).

### Q14: How does Moviq prevent Path Traversal attacks during local video serving?
**Answer**: Local media endpoints verify that resolved file paths strictly start with `os.path.abspath(STORAGE_DIR)`. Access attempts using `..` path traversal are immediately rejected with HTTP 404/422 status codes.

---

## Section 5: React & Frontend Architecture

### Q15: How does the frontend handle real-time generation status tracking?
**Answer**: The React frontend uses stage-aware polling via `MoviqApiClient.pollGenerationStatus()`. While the job is active (`QUEUED`, `SUBMITTED`, `GENERATING`, `PROCESSING`), it polls `GET /api/v1/generations/{id}` every 2 seconds, updating state machine progress bars and timeline event lists until `COMPLETED` or `FAILED`.

### Q16: How is state managed in the React application?
**Answer**: Workspace state (prompt, selected model, style preset, aspect ratio, duration, negative prompt, smart failover toggle) is managed in `App.tsx` and passed via typed props to modular components (`PromptComposer`, `AIDirector`, `StyleSelector`, `AdvancedSettings`, `VideoPreview`, `ProviderHealthPage`).

---

## Section 6: Testing & Quality Assurance

### Q17: What is the test coverage of Moviq?
**Answer**: Moviq features an **87-test automated Pytest suite** achieving **100% pass rate**. Tests cover provider factory routing, API error taxonomy, computer vision MP4 validation, health telemetry, microsecond timeline logging, security SSRF boundaries, and 25-job stress concurrency.

---

## Summary Matrix of Interview Talking Points

- **Primary Architecture**: Factory Pattern + Provider Abstraction + Asynchronous Polling Pipeline.
- **Computer Vision**: OpenCV frame motion difference validation (`absdiff`).
- **Resilience**: Idempotency keys + 45s TTL telemetry cache + Optional Smart Failover.
- **Security**: SSRF validation + Path traversal boundary checks + Backend-only credential isolation.
