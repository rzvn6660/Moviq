# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 2.1.x   | :white_check_mark: |
| 2.0.x   | :white_check_mark: |
| < 2.0   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability within Moviq, please follow these guidelines:

1. **Do NOT open a public GitHub issue**.
2. Email security report details directly to `security@moviq.ai` or contact the maintainers privately.
3. Include detailed steps to reproduce the vulnerability, along with any relevant proof-of-concept code or HTTP logs.
4. The maintainers will respond within 48 hours and work with you to resolve the issue before public disclosure.

---

## Security Architecture Summary

- **Backend Credential Protection**: API keys (`KIE_API_KEY`, `HF_TOKEN`, `LUMA_API_KEY`, `HAILUO_API_KEY`) remain strictly backend-only. Never exposed in responses or client JS bundles.
- **SSRF Protection**: Remote video download endpoints validate domain destinations against unsafe loopback (`127.0.0.1`, `localhost`) and private subnet IPs.
- **Path Traversal Protection**: Media serving endpoints strictly enforce path boundary checks preventing arbitrary file access.
- **Input Validation**: FastAPI Pydantic schemas sanitize prompt lengths, aspect ratios, and durations.
