from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional
from enum import Enum


class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class BookingCreate(BaseModel):
    destination_id: int = Field(..., description="ID of the travel destination")
    check_in: date = Field(..., description="Check-in date")
    check_out: date = Field(..., description="Check-out date")
    guests: int = Field(default=1, ge=1, le=10)
    special_requests: Optional[str] = Field(None, max_length=500)


class BookingResponse(BaseModel):
    id: int
    user_id: int
    destination_id: int
    check_in: date
    check_out: date
    guests: int
    status: BookingStatus
    total_price: float
    special_requests: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
