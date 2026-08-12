"""Itinerary data model and schemas."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ItineraryActivity(BaseModel):
    """Single activity within a day."""
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=1000)
    start_time: str = Field(default="09:00", description="Start time (HH:MM)")
    end_time: str = Field(default="10:00", description="End time (HH:MM)")
    location: str = Field(default="", description="Activity location")
    category: str = Field(default="sightseeing", description="Activity category")
    estimated_cost: float = Field(default=0.0, ge=0, description="Estimated cost in USD")
    notes: str = Field(default="", max_length=500)
    booking_url: str = Field(default="", description="Booking link if applicable")
    order: int = Field(default=0, ge=0, description="Sort order within the day")


class ItineraryDay(BaseModel):
    """A single day in the itinerary."""
    day_number: int = Field(..., ge=1, description="Day number (1-indexed)")
    date: Optional[str] = Field(None, description="Specific date (YYYY-MM-DD)")
    title: str = Field(default="", max_length=200, description="Day title or theme")
    activities: List[ItineraryActivity] = Field(default_factory=list)
    notes: str = Field(default="", max_length=1000)
    accommodation: str = Field(default="", description="Where to stay")
    total_budget: float = Field(default=0.0, ge=0)


class Itinerary(BaseModel):
    """Full itinerary document model."""
    id: Optional[str] = Field(None, alias="_id")
    user_id: str = Field(..., description="Owner user ID")
    title: str = Field(..., min_length=1, max_length=200, description="Trip title")
    description: str = Field(default="", max_length=2000)
    destination: str = Field(..., min_length=1, description="Primary destination")
    destinations: List[str] = Field(default_factory=list, description="All destinations")
    start_date: str = Field(..., description="Trip start date (YYYY-MM-DD)")
    end_date: str = Field(..., description="Trip end date (YYYY-MM-DD)")
    days: List[ItineraryDay] = Field(default_factory=list)
    total_budget: float = Field(default=0.0, ge=0, description="Total trip budget in USD")
    currency: str = Field(default="USD", description="Budget currency")
    travelers: int = Field(default=1, ge=1, le=20, description="Number of travelers")
    travel_style: str = Field(default="moderate", description="Budget/moderate/luxury")
    status: str = Field(default="draft", description="draft/planned/in_progress/completed")
    is_public: bool = Field(default=False, description="Publicly visible")
    tags: List[str] = Field(default_factory=list)
    cover_image: str = Field(default="", description="Cover image URL")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True


class ItineraryCreate(BaseModel):
    """Schema for creating a new itinerary."""
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)
    destination: str = Field(..., min_length=1)
    destinations: List[str] = Field(default_factory=list)
    start_date: str = Field(..., description="YYYY-MM-DD")
    end_date: str = Field(..., description="YYYY-MM-DD")
    total_budget: float = Field(default=0.0, ge=0)
    currency: str = Field(default="USD")
    travelers: int = Field(default=1, ge=1, le=20)
    travel_style: str = Field(default="moderate")
    tags: List[str] = Field(default_factory=list)
