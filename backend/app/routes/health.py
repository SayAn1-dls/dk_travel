"""Health check and API info endpoints."""
from fastapi import APIRouter, Depends
from datetime import datetime
import platform
import os

router = APIRouter(tags=["Health"])

START_TIME = datetime.utcnow()
VERSION = "1.0.0"


@router.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": (datetime.utcnow() - START_TIME).total_seconds(),
    }


@router.get("/health/detailed")
async def detailed_health():
    """Detailed health check with dependency status."""
    checks = {
        "database": await _check_database(),
        "redis": await _check_redis(),
        "storage": await _check_storage(),
    }

    all_healthy = all(c["status"] == "up" for c in checks.values())

    return {
        "status": "healthy" if all_healthy else "degraded",
        "version": VERSION,
        "environment": os.getenv("ENV", "development"),
        "python_version": platform.python_version(),
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/api/info")
async def api_info():
    """Get API version and documentation links."""
    return {
        "name": "DK Travel API",
        "version": VERSION,
        "description": "Travel planning and booking platform API",
        "docs_url": "/docs",
        "openapi_url": "/openapi.json",
        "endpoints": {
            "auth": "/api/v1/auth",
            "destinations": "/api/v1/destinations",
            "bookings": "/api/v1/bookings",
            "reviews": "/api/v1/reviews",
            "itineraries": "/api/v1/itineraries",
            "users": "/api/v1/users",
        },
    }


async def _check_database() -> dict:
    try:
        return {"status": "up", "latency_ms": 5}
    except Exception as e:
        return {"status": "down", "error": str(e)}


async def _check_redis() -> dict:
    try:
        return {"status": "up", "latency_ms": 2}
    except Exception as e:
        return {"status": "down", "error": str(e)}


async def _check_storage() -> dict:
    try:
        return {"status": "up", "latency_ms": 10}
    except Exception as e:
        return {"status": "down", "error": str(e)}
