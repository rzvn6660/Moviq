from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.core.exceptions import MoviqException
from app.db.base import Base
from app import db as db_module
from app.api.router import api_router
from app.models.generation import Generation
from app.schemas.common import GenerationStatus
from datetime import datetime, timezone
import json


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup logging & Database tables
    setup_logging()
    logger.info("Initializing Moviq database tables...")
    active_engine = db_module.session.engine
    Base.metadata.create_all(bind=active_engine)

    # Migration check for execution_mode, is_favorite, and favorite_at columns on SQLite tables
    try:
        with active_engine.connect() as conn:
            try:
                conn.execute(text("ALTER TABLE generations ADD COLUMN execution_mode VARCHAR"))
            except Exception:
                pass
            try:
                conn.execute(text("ALTER TABLE generations ADD COLUMN is_favorite BOOLEAN DEFAULT 0"))
            except Exception:
                pass
            try:
                conn.execute(text("ALTER TABLE generations ADD COLUMN favorite_at DATETIME"))
            except Exception:
                pass
            try:
                conn.execute(text("ALTER TABLE generations ADD COLUMN fidelity_score FLOAT DEFAULT 0.92"))
            except Exception:
                pass
            try:
                conn.execute(text("ALTER TABLE generations ADD COLUMN fidelity_label VARCHAR DEFAULT 'High Fidelity'"))
            except Exception:
                pass
            conn.commit()
    except Exception:
        pass  # Column already exists or migration non-critical

    # Initialize database session
    db = db_module.session.SessionLocal()
    try:
        pass
    finally:
        db.close()

    yield
    logger.info("Shutting down Moviq backend engine...")


app = FastAPI(
    title="Moviq AI Video Studio API",
    description="Backend API for Moviq AI Video Studio — Turn Ideas Into Motion.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition", "Content-Length", "Accept-Ranges", "Content-Type"],
)

# Exception Handlers
@app.exception_handler(MoviqException)
async def moviq_exception_handler(request: Request, exc: MoviqException):
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail,
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An internal server error occurred.",
                "retryable": True
            }
        },
    )

# Include Router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)
