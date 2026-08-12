"""Booking API routes."""

from datetime import datetime
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional

from backend.services.booking_service import BookingService

router = APIRouter()
booking_service = BookingService()


class CreateBookingRequest(BaseModel):
    destination_id: str
    check_in: datetime
    check_out: datetime
    guests: int = Field(default=1, ge=1, le=10)
    special_requests: Optional[str] = None


class CancelBookingRequest(BaseModel):
    reason: str = ""


@router.post("/", status_code=201)
async def create_booking(request: CreateBookingRequest, user_id: str = "demo-user"):
    """Create a new travel booking."""
    try:
        booking = await booking_service.create_booking(
            user_id=user_id,
            destination_id=request.destination_id,
            check_in=request.check_in,
            check_out=request.check_out,
            guests=request.guests,
            special_requests=request.special_requests,
        )
        return {"message": "Booking created", "booking": booking}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/")
async def list_bookings(
    user_id: str = "demo-user",
    status: Optional[str] = Query(None),
):
    """List all bookings for the current user."""
    bookings = await booking_service.get_user_bookings(user_id, status=status)
    return {"bookings": bookings, "count": len(bookings)}


@router.get("/{booking_id}")
async def get_booking(booking_id: str):
    """Get a specific booking by ID."""
    booking = await booking_service.get_booking(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking


@router.post("/{booking_id}/cancel")
async def cancel_booking(booking_id: str, request: CancelBookingRequest):
    """Cancel an existing booking."""
    success = await booking_service.cancel_booking(booking_id, request.reason)
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Cannot cancel: booking not found or already processed",
        )
    return {"message": "Booking cancelled", "booking_id": booking_id}


@router.post("/{booking_id}/confirm")
async def confirm_booking(booking_id: str, payment_id: str):
    """Confirm a booking after payment."""
    success = await booking_service.confirm_booking(booking_id, payment_id)
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Cannot confirm: booking not found or not pending",
        )
    return {"message": "Booking confirmed", "booking_id": booking_id}
