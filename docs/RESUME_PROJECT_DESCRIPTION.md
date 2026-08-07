# Moviq — Resume & Technical Portfolio Assets

---

## 1. One-Liner (Short Version)
> Architected **Moviq**, a modular AI video generation platform with FastAPI, React, PyTorch, and OpenCV supporting 6 AI video providers with live health telemetry and automated video validation.

---

## 2. Paragraph (Medium Version)
> Designed and built **Moviq**, a full-stack open-source AI video generation studio that abstracts multiple commercial and open-source video models (Kie.ai, Luma AI, Hailuo AI, Hugging Face, Wan, LTX Video) behind a unified, provider-independent backend. Implemented live provider health telemetry, a rule-based AI recommendation engine, smart failover, H.264 MP4 delivery pipeline, and perceptual frame motion validation using OpenCV.

---

## 3. Detailed Technical Bullet Points (ATS-Friendly)
- **Multi-Provider Architecture**: Built a decoupled provider abstraction layer in FastAPI/Python supporting 6 AI video providers (`Kie.ai`, `Luma AI`, `Hailuo AI`, `Hugging Face`, `Remote Wan`, `LTX Video`) with deterministic routing and zero silent provider substitution.
- **Provider Intelligence Telemetry**: Developed real-time telemetry dashboard monitoring ping latency, queue status, authentication verification, and documented credit balances with an async 45-second TTL cache lock.
- **Computer Vision & Video Pipeline**: Implemented an end-to-end MP4 validation pipeline using OpenCV (`cv2`) that computes frame perceptual motion difference (`absdiff`) to detect and reject static images disguised as videos.
- **Resilience & Smart Failover**: Engineered idempotent job processing (`Idempotency-Key` headers) and optional Smart Failover retries that transparently attempt secondary provider backplanes while recording microsecond audit events in SQLite/SQLAlchemy.
- **Modern React & TypeScript UI**: Built a dark-mode glassmorphism web interface using React 18, Vite, TypeScript, and Lucide icons featuring an AI Director prompt enhancer, live generation timeline, and provider operations dashboard.
- **Test Automation & Quality**: Created an 87-test automated test suite achieving 100% test pass rate across backend routing, error handling, stress concurrency (25 consecutive jobs), and security boundaries.

---

## 4. Technical Stack
- **Backend**: Python 3.11/3.13, FastAPI, SQLAlchemy, SQLite, Pydantic v2, PyTorch, OpenCV (`opencv-python-headless`), HTTPX, Pytest.
- **Frontend**: React 18, TypeScript 5, Vite, Vanilla Tailwind-styled CSS, Lucide React.
- **DevOps & Architecture**: REST API, Docker-ready, CORS Security, SSRF Mitigation, OpenAPI / Swagger.
