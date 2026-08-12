"""Hotel data model and schemas."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class HotelLocation(BaseModel):
    """Hotel location details."""
    address: str = Field(..., description="Street address")
    city: str = Field(..., description="City name")
    country: str = Field(..., description="Country name")
    latitude: float = Field(default=0.0, description="Latitude coordinate")
    longitude: float = Field(default=0.0, description="Longitude coordinate")
    zip_code: str = Field(default="", description="ZIP or postal code")


class HotelRoom(BaseModel):
    """Hotel room type."""
    room_type: str = Field(..., description="Type of room (Standard, Deluxe, Suite)")
    price_per_night: float = Field(..., ge=0, description="Price per night in USD")
    max_guests: int = Field(default=2, ge=1, description="Maximum number of guests")
    bed_type: str = Field(default="Queen", description="Bed type")
    available: bool = Field(default=True, description="Room availability")


class Hotel(BaseModel):
    """Full hotel document model."""
    id: Optional[str] = Field(None, alias="_id", description="MongoDB document ID")
    name: str = Field(..., min_length=1, max_length=200, description="Hotel name")
    description: str = Field(default="", max_length=2000, description="Hotel description")
    star_rating: int = Field(..., ge=1, le=5, description="Star rating (1-5)")
    location: HotelLocation
    amenities: List[str] = Field(default_factory=list, description="List of amenities")
    rooms: List[HotelRoom] = Field(default_factory=list, description="Available room types")
    images: List[str] = Field(default_factory=list, description="Image URLs")
    contact_email: str = Field(default="", description="Contact email")
    contact_phone: str = Field(default="", description="Contact phone")
    website: str = Field(default="", description="Hotel website URL")
    average_rating: float = Field(default=0.0, ge=0, le=5, description="Average user rating")
    total_reviews: int = Field(default=0, ge=0, description="Total number of reviews")
    is_featured: bool = Field(default=False, description="Featured hotel flag")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "name": "The Grand Palace Hotel",
                "description": "Luxury 5-star hotel in the heart of Paris",
                "star_rating": 5,
                "location": {
                    "address": "123 Champs-Elysees",
                    "city": "Paris",
                    "country": "France",
                    "latitude": 48.8566,
                    "longitude": 2.3522,
                },
                "amenities": ["WiFi", "Pool", "Spa", "Restaurant"],
            }
        }


class HotelCreate(BaseModel):
    """Schema for creating a new hotel."""
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)
    star_rating: int = Field(..., ge=1, le=5)
    location: HotelLocation
    amenities: List[str] = Field(default_factory=list)
    rooms: List[HotelRoom] = Field(default_factory=list)
    images: List[str] = Field(default_factory=list)
    contact_email: str = Field(default="")
    contact_phone: str = Field(default="")
    website: str = Field(default="")


class HotelResponse(BaseModel):
    """Hotel API response."""
    id: str
    name: str
    description: str
    star_rating: int
    location: HotelLocation
    amenities: List[str]
    rooms: List[HotelRoom]
    price_range: str = Field(default="", description="Formatted price range")
    average_rating: float
    total_reviews: int
    is_featured: bool
    images: List[str]


class HotelSearchParams(BaseModel):
    """Search parameters for hotel queries."""
    destination: Optional[str] = Field(None, description="City or country")
    check_in: Optional[str] = Field(None, description="Check-in date (YYYY-MM-DD)")
    check_out: Optional[str] = Field(None, description="Check-out date (YYYY-MM-DD)")
    guests: int = Field(default=2, ge=1, le=10)
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)
    min_rating: Optional[int] = Field(None, ge=1, le=5)
    amenities: Optional[List[str]] = None
    sort_by: str = Field(default="price", description="Sort field")
    sort_order: str = Field(default="asc", description="Sort order (asc/desc)")
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
