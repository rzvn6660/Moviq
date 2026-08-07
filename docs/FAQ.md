# Frequently Asked Questions (FAQ)

### Q: What is Moviq?
A: Moviq is an open-source AI video generation studio that transforms text prompts into cinematic videos through a unified provider-independent backend architecture.

### Q: Which AI video models are supported?
A: Moviq supports 6 provider backplanes out of the box:
- **Kie.ai**: Kling 3.0 Pro, Wan 2.1, Google Veo 3.1
- **Luma AI**: Dream Machine
- **Hailuo AI**: MiniMax Video 01
- **Hugging Face**: Wan 2.2 Serverless Inference
- **Remote Wan**: Self-hosted CUDA GPU Worker
- **LTX Video**: Local PyTorch GPU Engine

### Q: Can I run Moviq completely offline without paid API keys?
A: Yes! Moviq supports:
1. `VIDEO_PROVIDER=mock` for simulated generations.
2. `ENABLE_SYNTHETIC_FALLBACK=true` for local synthetic MP4 rendering using OpenCV.
3. `LTX Video` or `Remote Wan` for running on local CUDA GPUs.

### Q: How does Video Validation v2 work?
A: Every generated video undergoes OpenCV frame inspection. Moviq checks box headers, duration, and frame perceptual motion difference (`cv2.absdiff`) to reject static images disguised as videos.

### Q: Is Moviq ready for production deployment?
A: Yes, Moviq includes comprehensive API schema validation, path traversal protection, SSRF protection, rate limiting, and 100% test coverage.
