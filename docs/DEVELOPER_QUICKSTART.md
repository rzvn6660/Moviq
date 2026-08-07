# Developer Quickstart Guide

This guide walks through setting up Moviq locally for development and testing.

---

## Prerequisites

- **Python**: 3.11 or higher
- **Node.js**: 18.0 or higher
- **OpenCV Dependencies**: `opencv-python-headless` (included in `requirements.txt`)

---

## 1. Backend Quickstart

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env

# Run FastAPI dev server
uvicorn app.main:app --port 8001 --reload
```

FastAPI Interactive API docs will be available at: `http://localhost:8001/docs`

---

## 2. Frontend Quickstart

```bash
# In repository root
npm install

# Start Vite dev server
npm run dev
```

Web interface will be available at: `http://localhost:5173`

---

## 3. Running Test Suite

```bash
cd backend
venv/Scripts/python.exe -m pytest tests/
```
