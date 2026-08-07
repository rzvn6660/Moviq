# Moviq v3.0.1 — Initial Public Release Notes

> **Tag**: `v3.0.1`  
> **Release Name**: Moviq v3.0.1 — Initial Public Release  
> **Target Branch**: `main`  
> **Date**: August 2026  

---

## 🚀 Release Highlights

- **Multi-Provider Architecture**: Unified backplane supporting 6 video providers (`Kie.ai`, `Luma AI`, `Hailuo AI`, `Hugging Face`, `Remote Wan`, `LTX Video`).
- **Provider Health Telemetry**: Live ping latency, queue status, and credential verification with an async 45-second TTL cache lock.
- **AI Recommendation Engine**: Rule-based prompt semantics engine matching optimal models based on visual themes (cars → Kling, nature → Luma, anime → Hailuo).
- **Optional Smart Failover**: Automatic fallback provider sequence with microsecond audit event timeline logging.
- **Computer Vision Video Validation (v2)**: OpenCV frame-difference motion analysis (`absdiff`) that automatically detects and rejects static images disguised as MP4s.
- **Microsecond Observability Timeline**: 13-stage execution audit trail tracking every step from prompt submission to thumbnail extraction.

---

## 📊 Provider Capability Matrix

| Provider | Model ID | Execution Mode | Supported Aspect Ratios | Max Duration |
| :--- | :--- | :--- | :--- | :--- |
| **Kie.ai** | `kling-3.0/video` | Hosted API | `16:9`, `9:16`, `1:1` | 10s |
| **Luma AI** | `dream-machine` | Hosted API | `16:9`, `9:16`, `1:1` | 5s |
| **Hailuo AI** | `hailuo-01` | Hosted API | `16:9`, `9:16`, `1:1` | 5s |
| **Hugging Face** | `Wan-AI/Wan2.2-TI2V-5B` | Serverless Inference | `16:9` | 5s |
| **Remote Wan** | `Wan-AI/Wan2.1-T2V-1.3B-Diffusers` | Self-Hosted CUDA | `16:9` | 5s |
| **LTX Video** | `ltx-video` | Local PyTorch GPU | `16:9` | 5s |

---

## 🧪 Verification & Quality Control

- **Backend Pytest Suite**: 87 / 87 Passed (100%)
- **Frontend Production Build**: `tsc -b` & `vite build` (0 Errors)
- **OpenCV Safety**: All VideoCapture/VideoWriter handles wrapped in `try/finally` blocks.

---

## ⚙️ Upgrade & Setup Instructions

```bash
git clone https://github.com/rzvn6660/Moviq.git
cd Moviq

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --port 8001 --reload

# Frontend setup (in repository root)
npm install
npm run dev
```
