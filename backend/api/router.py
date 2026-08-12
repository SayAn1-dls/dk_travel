"""Main API router that aggregates all route modules."""

from fastapi import APIRouter

from .health import router as health_router
from .destinations import router as destinations_router
from .bookings import router as bookings_router
from .auth import router as auth_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health_router, tags=["Health"])
api_router.include_router(destinations_router, prefix="/destinations", tags=["Destinations"])
api_router.include_router(bookings_router, prefix="/bookings", tags=["Bookings"])
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
