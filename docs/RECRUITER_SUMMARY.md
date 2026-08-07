# Moviq — Executive Recruiter & Hiring Summary

---

## 📌 Executive Summary
**Moviq** is an open-source AI video generation studio built with **React 18, TypeScript, FastAPI, PyTorch, and OpenCV**. It abstracts 6 AI video provider backplanes behind a unified service layer, featuring real-time health telemetry, rule-based AI provider recommendations, smart failover, H.264 MP4 container delivery, and computer vision frame motion validation.

---

## 🎯 Candidate Core Competencies Demonstrated

### 1. Full-Stack Systems Architecture
- Designed a decoupled, provider-independent backend architecture in FastAPI/Python that routes text-to-video jobs across 6 commercial and open-source AI engines (`Kie.ai`, `Luma AI`, `Hailuo AI`, `Hugging Face`, `Remote Wan`, `LTX Video`).
- Built a modern, dark-mode glassmorphism web interface using React 18, Vite, TypeScript, and Tailwind-styled Vanilla CSS.

### 2. Computer Vision & Media Engineering
- Engineered a production MP4 validation pipeline using OpenCV (`cv2`) that analyzes box container headers, video stream framerates, and perceptual frame motion difference (`absdiff`) to reject static images disguised as MP4s.

### 3. High-Throughput Performance & Telemetry
- Implemented an async 45-second TTL health cache lock preventing API rate limits.
- Built a 13-stage microsecond event timeline tracking every generation lifecycle step.

### 4. Production Quality Assurance & Security
- Created an 87-test automated Pytest suite with **100% pass rate**.
- Enforced security controls: backend-only credential isolation, SSRF download protection, path traversal shielding, and request idempotency.

---

## 🛠️ Technology Keyword Index
`Python 3.11/3.13` • `FastAPI` • `React 18` • `TypeScript` • `Vite` • `PyTorch` • `OpenCV` • `SQLAlchemy` • `SQLite` • `REST API` • `OpenAPI` • `Docker-ready` • `Pytest` • `SSRF Mitigation` • `Computer Vision` • `LLM Prompt Engineering`
