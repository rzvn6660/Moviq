# MOVIQ — ASSESSMENT DOCUMENTATION
## AI/ML Engineer Internship Assessment Summary

**Tagline**: *Turn Ideas Into Motion.*  
**Author**: Candidate Engineer  
**Project**: Moviq AI Video Creation Studio  
**Reading Time**: ~3 minutes

---

## 1. Problem Statement & Executive Summary

Generative video models require highly specific, structured prompt parameters (camera framing, lighting ratios, subject action, mood descriptors, and aspect ratios) to produce high-fidelity motion. Raw user prompts often result in distorted, static, or incoherent video generation.

**Moviq** solves this by bridging the gap between raw human ideas and diffusion model execution through a two-stage architecture:
1. **AI Director Stage**: Transforms simple text prompts into structured cinematic direction using **Groq (`openai/gpt-oss-120b`)** with JSON Schema Structured Outputs and a deterministic Python `PromptScorer`.
2. **Multi-Provider Video Engine Stage**: Orchestrates video rendering across **`MockVideoProvider`**, **`FalVideoProvider`**, **`HuggingFaceVideoProvider`**, and **`WanVideoProvider`** (open-source Wan2.1 T2V 1.3B).

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
         │     DirectorProvider      │                   │       VideoProvider       │
         └─────────────┬─────────────┘                   └─────────────┬─────────────┘
                       │                                               │
         ┌─────────────┴─────────────┐         ┌───────────────┬───────┴───────┬───────────────┐
         ▼                           ▼         ▼               ▼               ▼               ▼
┌─────────────────┐         ┌─────────┐   ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│ Groq AI Director│         │ Mock    │   │ Wan2.1  │     │ Fal-ai  │     │ Hugging │     │ Mock    │
│ gpt-oss-120b    │         │ Director│   │ Local   │     │ Kling   │     │ Face    │     │ Video   │
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

### B. Wan2.1 T2V 1.3B Open-Source Diffusion Engine
- Integrated via `WanVideoProvider` (`Wan-AI/Wan2.1-T2V-1.3B-Diffusers`).
- Standalone live-validated environment on **Kaggle Tesla P100 16GB GPU**:
  - **Frameworks**: PyTorch `2.7.1+cu118`, Diffusers `0.35.2`, Transformers `4.57.1`.
  - **Render Profile**: `576 × 320` resolution, `33` frames @ `16` FPS ($\approx 2.06$s output clip), `20` inference steps, `float16` precision.
  - **Memory Safeguards**: `enable_model_cpu_offload()` and `enable_vae_tiling()` prevent CUDA Out-Of-Memory errors on 16GB GPUs without compiling native CUDA extensions (`flash-attn`).

---

## 4. Key Engineering Differentiators

1. **Provider Abstraction**: Unified `VideoProvider` contract (`submit_generation`, `check_status`, `get_result`) abstracts cloud queues, local GPUs, and mock providers.
2. **Backend-Enforced Idempotency**: UUID request tracking via `Idempotency-Key` headers backed by SQLite `UNIQUE` database constraints prevents duplicate job submissions.
3. **Truthful Asynchronous Progress**: Supports both percentage-based and stage-based progress (`QUEUED` → `SUBMITTED` → `GENERATING` → `PROCESSING` → `COMPLETED`) without fabricating artificial percentages.
4. **Lazy ML Dependency Loading**: Heavy ML packages (`torch`, `diffusers`) load dynamically *only* when `WanVideoProvider` is invoked. Standard server startup remains fast and lightweight.
5. **Security & Memory Safety**: Downloads use chunked streaming with strict SSRF validation (`is_safe_download_url()`), path traversal boundary checks, and zero API key leakage to client bundles.

---

## 5. Verification & Testing

- **Backend Test Suite**: **53 out of 53 tests passed** (`python -m pytest` in 11.18s).
- **Frontend Compilation**: Production build (`npm run build`) **passed cleanly in 2.25s** with 0 errors.

### Running Quick Commands
```bash
# Backend Test Suite
cd backend
venv\Scripts\python -m pytest

# Frontend Production Build
npm run build
```

---

## 6. Known Limitations
- Local Wan2.1 rendering requires a CUDA GPU and optional dependencies (`backend/requirements-wan.txt`).
- Kaggle was utilized as a standalone compute environment for hardware validation, not as a live production API endpoint.
