"""Data models for Wanderly backend."""

from .hotel import Hotel, HotelCreate, HotelResponse, HotelSearchParams
from .itinerary import Itinerary, ItineraryCreate, ItineraryDay, ItineraryActivity
from .review import Review, ReviewCreate, ReviewResponse
from .blog_post import BlogPost, BlogPostCreate, BlogPostResponse

__all__ = [
    "Hotel", "HotelCreate", "HotelResponse", "HotelSearchParams",
    "Itinerary", "ItineraryCreate", "ItineraryDay", "ItineraryActivity",
    "Review", "ReviewCreate", "ReviewResponse",
    "BlogPost", "BlogPostCreate", "BlogPostResponse",
]
