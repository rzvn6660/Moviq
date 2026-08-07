# 🚀 Announcing Moviq v3.0 — Modular AI Video Generation Studio

I'm thrilled to release **Moviq v3.0**, an open-source AI video generation platform designed with a provider-independent backend architecture!

---

## 🎬 Why Moviq?

Working with AI video models (Kling, Luma, MiniMax Hailuo, Wan, LTX Video) often means battling fragmented APIs, raw exception leaks, and static image fallbacks. Moviq abstracts 6 AI provider backplanes behind a unified FastAPI service layer and React 18 web interface.

---

## 🔥 Key Technical Capabilities

1. **Multi-Provider Architecture**: Unified backplane supporting Kie.ai (Kling 3.0, Veo 3.1), Luma AI (Dream Machine), Hailuo AI (MiniMax), Hugging Face (Wan 2.2), Remote Wan, and local LTX Video.
2. **Live Telemetry & Provider Health**: Real-time monitoring of latency, queue traffic, and credential health using an async 45-second TTL cache lock.
3. **AI Recommendation Engine**: Rule-based prompt semantics engine matching optimal models based on visual themes (cars → Kling, nature → Luma, anime → Hailuo).
4. **Computer Vision Video Validation**: OpenCV frame-difference motion analysis (`absdiff`) that automatically detects and rejects static images disguised as MP4s.
5. **Full Observability**: 13-stage microsecond event timeline recording every step from prompt submission to thumbnail extraction.
6. **Smart Failover**: Automatic fallback provider sequence with full event logging. Zero silent substitutions.

---

## 🛠️ Tech Stack
- **Backend**: Python, FastAPI, SQLAlchemy, SQLite, PyTorch, OpenCV (`opencv-python-headless`), HTTPX, Pytest.
- **Frontend**: React 18, TypeScript, Vite, Vanilla CSS, Lucide React.
- **Testing**: 87-test automated test suite (100% pass rate).

---

## 🔗 Open Source & Links
Explore the code, architecture diagrams, and quickstart documentation on GitHub!

👉 GitHub Repository: https://github.com/rzvn6660/Moviq  
👉 Documentation: https://github.com/rzvn6660/Moviq#readme  

#AI #MachineLearning #Python #FastAPI #React #TypeScript #OpenCV #ComputerVision #GenerativeAI #VideoAI #OpenSource #SoftwareEngineering #PyTorch
