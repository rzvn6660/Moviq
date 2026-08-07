# Changelog

All notable changes to Moviq will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [v2.1.5] - 2026-08-07 - Release Candidate 2 (RC2)

### Added
- **Live Provider Health Telemetry**: Live ping latency, queue status, credential checks, and 45s TTL cache.
- **AI Provider Recommendation Engine**: Semantic keyword & preference rule evaluator.
- **Optional Smart Failover**: Transparent provider retries with full `GenerationEvent` logging.
- **Empirical Provider Benchmarks**: Measured runtime, queue, success rate, and quality scores.
- **Cost & Runtime Estimator**: Documented per-second pricing and credit calculation.
- **Perceptual Motion Validation (v2)**: OpenCV frame-diff analysis rejecting motionless static MP4s.

### Fixed
- Standardized OpenCV `VideoCapture` and `VideoWriter` resource cleanup via `try/finally` blocks.
- Unified provider exception hierarchy under `app.core.exceptions`.
- Standardized backend configuration in `app.core.config.settings`.

---

## [v2.0.0] - 2026-08-06

### Added
- Multi-provider architecture supporting Kie.ai, Luma AI, Hailuo AI, Hugging Face, Remote Wan, LTX Video.
- Provider abstraction layer (`BaseVideoProvider`).
- Unified H.264 MP4 delivery pipeline with `Content-Disposition`.
- Real-time generation timeline and technical observability inspector.
