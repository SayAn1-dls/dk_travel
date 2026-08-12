"""Review data model and schemas."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ReviewAuthor(BaseModel):
    """Review author information."""
    user_id: str = Field(..., description="Author user ID")
    name: str = Field(..., description="Display name")
    avatar: str = Field(default="", description="Avatar URL")


class ReviewHelpfulness(BaseModel):
    """Review helpfulness tracking."""
    helpful_count: int = Field(default=0, ge=0)
    not_helpful_count: int = Field(default=0, ge=0)


class Review(BaseModel):
    """Full review document model."""
    id: Optional[str] = Field(None, alias="_id")
    entity_type: str = Field(..., description="Type: hotel, destination, restaurant, activity")
    entity_id: str = Field(..., description="ID of the reviewed entity")
    author: ReviewAuthor
    rating: int = Field(..., ge=1, le=5, description="Rating (1-5 stars)")
    title: str = Field(default="", max_length=200, description="Review title")
    content: str = Field(..., min_length=10, max_length=5000, description="Review text")
    pros: List[str] = Field(default_factory=list, description="Positive points")
    cons: List[str] = Field(default_factory=list, description="Negative points")
    photos: List[str] = Field(default_factory=list, description="Photo URLs")
    visit_date: Optional[str] = Field(None, description="When the visit occurred")
    travel_type: str = Field(default="leisure", description="leisure/business/family/solo")
    helpfulness: ReviewHelpfulness = Field(default_factory=ReviewHelpfulness)
    is_verified: bool = Field(default=False, description="Verified purchase/visit")
    status: str = Field(default="published", description="published/pending/flagged")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True


class ReviewCreate(BaseModel):
    """Schema for creating a new review."""
    entity_type: str = Field(..., description="hotel, destination, restaurant, activity")
    entity_id: str = Field(..., description="ID of entity being reviewed")
    rating: int = Field(..., ge=1, le=5)
    title: str = Field(default="", max_length=200)
    content: str = Field(..., min_length=10, max_length=5000)
    pros: List[str] = Field(default_factory=list)
    cons: List[str] = Field(default_factory=list)
    visit_date: Optional[str] = None
    travel_type: str = Field(default="leisure")


class ReviewResponse(BaseModel):
    """Review API response."""
    id: str
    entity_type: str
    entity_id: str
    author: ReviewAuthor
    rating: int
    title: str
    content: str
    pros: List[str]
    cons: List[str]
    visit_date: Optional[str]
    travel_type: str
    helpfulness: ReviewHelpfulness
    is_verified: bool
    created_at: str


class ReviewStats(BaseModel):
    """Aggregated review statistics."""
    entity_id: str
    total_reviews: int = 0
    average_rating: float = 0.0
    rating_distribution: dict = Field(default_factory=lambda: {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0})
    recent_reviews: List[ReviewResponse] = Field(default_factory=list)
