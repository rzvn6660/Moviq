from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health", summary="Health Check", description="Returns backend status and service availability.")
async def get_health():
    return {
        "status": "ok",
        "service": "Moviq AI Video Backend Engine",
        "version": "1.0.0",
    }
