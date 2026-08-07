# Moviq Troubleshooting Guide

Common issues and solutions when running or developing Moviq locally.

---

## 1. Provider Credentials & Configuration

### Symptom: Provider status displays `CONFIG_MISSING` or `401 Unauthorized`
- **Cause**: Missing or default placeholder API keys in `backend/.env`.
- **Solution**:
  1. Open `backend/.env` (or root `.env`).
  2. Verify credentials for your target provider (`KIE_API_KEY`, `HF_TOKEN`, etc.).
  3. Alternatively, set `ENABLE_SYNTHETIC_FALLBACK=true` or `VIDEO_PROVIDER=mock` for offline local testing.

---

## 2. OpenCV & Video Frame Processing

### Symptom: `cv2.error: OpenCV(4.x.x) ... libGL.so.1: cannot open shared object file` (Linux Server)
- **Cause**: Missing system OpenGL libraries on headless Linux environments.
- **Solution**:
  ```bash
  sudo apt-get update && sudo apt-get install -y libgl1-mesa-glx libglib2.0-0
  ```

---

## 3. Database Connection or Locked State

### Symptom: `sqlite3.OperationalError: database is locked`
- **Cause**: Concurrent write transactions in SQLite during heavy multi-threaded test runs.
- **Solution**:
  Moviq uses connection pooling and WAL mode in SQLite. If developing under high concurrency, consider configuring PostgreSQL in `DATABASE_URL=postgresql://user:pass@localhost/moviq`.

---

## 4. Frontend API Connection Error

### Symptom: `Failed to fetch / Connection refused` on frontend
- **Cause**: Backend server is not running on port `8001`.
- **Solution**:
  Ensure the FastAPI server is running:
  ```bash
  cd backend
  uvicorn app.main:app --port 8001
  ```
