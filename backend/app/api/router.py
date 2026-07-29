from fastapi import APIRouter
from app.api import health, director, models, generations

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(director.router)
api_router.include_router(models.router)
api_router.include_router(generations.router)
