# MOVIQ — ASSESSMENT DOCUMENTATION
## AI/ML Engineer Internship Assessment Summary

**Tagline**: *Turn Ideas Into Motion.*  
**Author**: Candidate Engineer  
**Project**: Moviq AI Video Creation Studio  
**Reading Time**: ~3 minutes

---

## 1. Problem Statement & Executive Summary

Generative video models require highly specific, structured prompt parameters (camera framing, lighting ratios, subject action, mood descriptors, and aspect ratios) to produce high-fidelity motion. Raw user prompts often result in distorted, static, or incoherent video generation.

**Moviq** solves this by bridging the gap between raw human ideas and multi-provider generative video execution through a two-stage architecture:
1. **AI Director Stage**: Transforms simple text prompts into structured cinematic direction using **Groq (`openai/gpt-oss-120b`)** with JSON Schema Structured Outputs and a deterministic Python `PromptScorer`.
2. **Multi-Model / Multi-Provider Video Engine Stage**: Dynamic model routing across:
   - **Hosted Inference**: Hugging Face Inference API (`Wan-AI/Wan2.2-TI2V-5B` via `fal-ai` serverless router)
   - **Hosted API / Cloud Queue**: `fal-ai` open video models (`fal-ai/kling-video/v2.5-turbo/pro/text-to-video`, `hunyuan-video-v1`)
   - **Self-Hosted GPU**: Open-source CUDA GPU workers (`Wan-AI/Wan2.1-T2V-1.3B-Diffusers` via Kaggle/remote worker API)
   - **External Web Models**: Proprietary engines (`Pika 2.5`, `Dream Machine v2.5`, `Gen-3 Alpha`) with clean configuration badges and external website links
   - **Simulation**: Offline development simulation (`MockVideoProvider`)

---

## 2. System Architecture

```
                               ┌────────────────────────────────┐
                               │   React 18 + Vite + Tailwind   │
                               └───────────────┬────────────────┘
                                               │ HTTP / REST API (Axios + fetch)
                                               ▼
                               ┌────────────────────────────────┐
                               │   FastAPI Python Backend API   │
                               └───────────────┬────────────────┘
                                               │
                       ┌───────────────────────┴───────────────────────┐
                       ▼                                               ▼
         ┌───────────────────────────┐                   ┌───────────────────────────┐
         │     DirectorProvider      │                   │   get_video_provider()    │
         └─────────────┬─────────────┘                   └─────────────┬─────────────┘
                       │                                               │
         ┌─────────────┴─────────────┐         ┌───────────────┬───────┴───────┬───────────────┐
         ▼                           ▼         ▼               ▼               ▼               ▼
┌─────────────────┐         ┌─────────┐   ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│ Groq AI Director│         │ Mock    │   │ Wan2.2  │     │ Wan2.1  │     │ Fal-ai  │     │ Mock    │
│ gpt-oss-120b    │         │ Director│   │ HF Inst │     │ Remote  │     │ Kling   │     │ Video   │
└─────────────────┘         └─────────┘   └─────────┘     └─────────┘     └─────────┘     └─────────┘
                                               │
                                               ▼
                                  ┌──────────────────────────┐
                                  │ SQLite Persistence       │
                                  │ DB + Local Media Store   │
                                  └──────────────────────────┘
```

---

## 3. Core AI/ML Components

### A. Groq AI Director (`openai/gpt-oss-120b`)
- Implements strict **JSON Schema Structured Outputs** returning 6-axis camera direction (`subject`, `environment`, `action`, `camera`, `lighting`, `mood`).
- Evaluates raw vs enhanced prompt clarity using a deterministic 100-point `PromptScorer`.
- Fully decoupled via `DirectorProvider` interface with automatic fallback handling.

### B. Hosted Text-to-Video Inference (`Wan-AI/Wan2.2-TI2V-5B`)
- Integrated via `HuggingFaceVideoProvider` using Hugging Face Inference API (`fal-ai` serverless provider router).
- Executes real prompt-conditioned video generation without requiring local GPUs or manual worker setup.

### C. Wan2.1 T2V 1.3B Open-Source Diffusion Engine
- Integrated via `RemoteWanVideoProvider` and `WanVideoProvider` (`Wan-AI/Wan2.1-T2V-1.3B-Diffusers`).
- Standalone live-validated environment on **Kaggle Tesla P100 16GB GPU**:
  - **Frameworks**: PyTorch `2.7.1+cu118`, Diffusers `0.35.2`, Transformers `4.57.1`.
  - **Render Profile**: `576 × 320` resolution, `33` frames @ `16` FPS ($\approx 2.06$s output clip), `20` inference steps, `float16` precision.
  - **Memory Safeguards**: `enable_model_cpu_offload()` and `enable_vae_tiling()` prevent CUDA Out-Of-Memory errors on 16GB GPUs without compiling native CUDA extensions (`flash-attn`).

---

## 4. Key Engineering Differentiators

1. **Multi-Model / Multi-Provider Dynamic Factory**: `get_video_provider(model_id)` inspects `model_cap.provider` dynamically and instantiates the exact required provider class.
2. **Execution Mode & Availability Enforcement**: Models report execution modes (`HOSTED_INFERENCE`, `HOSTED_API`, `SELF_HOSTED`, `EXTERNAL_WEB`, `MOCK`) and configuration status (`READY` vs `NOT CONFIGURED`). Unconfigured or external models fail cleanly with clear error messages rather than silently reverting to demo videos.
3. **Persistent Execution Mode Metadata**: DB schema stores `execution_mode` on `Generation` records and passes it to the frontend `GenerationInspector`.
4. **Backend-Enforced Idempotency**: UUID request tracking via `Idempotency-Key` headers backed by SQLite `UNIQUE` database constraints prevents duplicate job submissions.
5. **Truthful Asynchronous Progress**: Supports both percentage-based and stage-based progress (`QUEUED` → `SUBMITTED` → `GENERATING` → `PROCESSING` → `COMPLETED`) without fabricating artificial percentages.
6. **Security & Memory Safety**: Downloads use chunked streaming with strict SSRF validation (`is_safe_download_url()`), path traversal boundary checks, and zero API key leakage to client bundles.

---

## 5. Verification & Testing

- **Backend Test Suite**: **66 out of 66 tests passed** (`python -m pytest` in 15.26s).
- **Frontend Compilation**: Production build (`npm run build`) **passed cleanly** with 0 errors.

### Running Quick Commands
```bash
# Backend Test Suite
cd backend
venv\Scripts\python -m pytest

# Frontend Production Build
npm run build
```
