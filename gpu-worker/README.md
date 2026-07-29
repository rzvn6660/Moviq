# Moviq Remote Wan2.1 GPU Worker Service

Standalone FastAPI worker service designed for deploying **Wan2.1 T2V 1.3B** (`Wan-AI/Wan2.1-T2V-1.3B-Diffusers`) on dedicated CUDA GPU instances (RunPod, Kaggle, Lambda Labs, Modal, or local GPU servers).

---

## ⚡ Deployment & Setup Instructions

### 1. Prerequisites
- Python 3.10+
- NVIDIA CUDA GPU with at least 16GB VRAM (e.g. Tesla P100, RTX 3090, RTX 4090, A10G)

### 2. Installation
```bash
cd gpu-worker
pip install -r requirements.txt
```

### 3. Environment Variables
```env
REMOTE_WAN_API_KEY=your_secret_bearer_token
WAN_MODEL_ID=Wan-AI/Wan2.1-T2V-1.3B-Diffusers
```

### 4. Running the Worker
```bash
uvicorn app:app --host 0.0.0.0 --port 8002
```

---

## 🔌 API Specification

- `GET /health`: Returns worker status, CUDA availability, and pipeline status.
- `POST /generate`: Accepts prompt payload and returns generated video URL (`Authorization: Bearer <REMOTE_WAN_API_KEY>` required).
- `GET /videos/{filename}`: Streams generated MP4 video file.
