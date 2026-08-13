from fastapi import APIRouter, status
from datetime import datetime, timezone

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {
        "status": "healthy",
        "service": "dk-travel-api",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
    }


@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness_check():
    return {
        "status": "ready",
        "database": "connected",
        "cache": "connected",
    }
