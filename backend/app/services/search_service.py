"""Search and filter service for travel destinations."""
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum
import re


class SortBy(Enum):
    PRICE_ASC = "price_asc"
    PRICE_DESC = "price_desc"
    RATING = "rating"
    POPULARITY = "popularity"
    DISTANCE = "distance"
    NAME = "name"


class TripType(Enum):
    ADVENTURE = "adventure"
    RELAXATION = "relaxation"
    CULTURAL = "cultural"
    WILDLIFE = "wildlife"
    BEACH = "beach"
    MOUNTAIN = "mountain"
    HERITAGE = "heritage"
    PILGRIMAGE = "pilgrimage"


@dataclass
class SearchFilters:
    query: str = ""
    min_price: float = 0
    max_price: float = float("inf")
    min_rating: float = 0
    trip_types: Optional[List[TripType]] = None
    state: Optional[str] = None
    max_distance_km: Optional[float] = None
    amenities: Optional[List[str]] = None
    sort_by: SortBy = SortBy.POPULARITY
    page: int = 1
    per_page: int = 20


class SearchService:
    """Full-text search and filtering for destinations."""

    def __init__(self, db_session, cache_client=None):
        self.db = db_session
        self.cache = cache_client

    async def search(
        self, filters: SearchFilters
    ) -> Dict[str, Any]:
        """Search destinations with filters and pagination."""
        cache_key = self._build_cache_key(filters)

        if self.cache:
            cached = await self.cache.get(cache_key)
            if cached:
                return cached

        results = await self._execute_search(filters)
        total = await self._count_results(filters)

        response = {
            "results": results,
            "total": total,
            "page": filters.page,
            "per_page": filters.per_page,
            "total_pages": (total + filters.per_page - 1) // filters.per_page,
            "filters_applied": self._serialize_filters(filters),
        }

        if self.cache:
            await self.cache.set(cache_key, response, ttl=300)

        return response

    async def autocomplete(self, query: str, limit: int = 5) -> List[str]:
        """Get autocomplete suggestions for search queries."""
        if len(query) < 2:
            return []
        pattern = re.compile(re.escape(query), re.IGNORECASE)
        suggestions = await self.db.find_matching(pattern, limit=limit)
        return suggestions

    async def get_trending(self, limit: int = 10) -> List[Dict]:
        """Get trending destinations based on recent searches."""
        return await self.db.get_trending_destinations(limit=limit)

    async def get_recommendations(
        self, user_id: str, limit: int = 5
    ) -> List[Dict]:
        """Get personalized recommendations based on user history."""
        history = await self.db.get_user_search_history(user_id)
        preferences = self._analyze_preferences(history)
        return await self.db.find_similar(preferences, limit=limit)

    def _build_cache_key(self, filters: SearchFilters) -> str:
        """Build a deterministic cache key from filters."""
        parts = [
            f"q:{filters.query}",
            f"p:{filters.min_price}-{filters.max_price}",
            f"r:{filters.min_rating}",
            f"s:{filters.sort_by.value}",
            f"pg:{filters.page}",
        ]
        return "search:" + "|".join(parts)

    def _serialize_filters(self, filters: SearchFilters) -> Dict:
        return {
            "query": filters.query,
            "price_range": [filters.min_price, filters.max_price],
            "min_rating": filters.min_rating,
            "sort_by": filters.sort_by.value,
        }

    def _analyze_preferences(self, history: List[Dict]) -> Dict:
        """Analyze search history to extract user preferences."""
        trip_type_counts: Dict[str, int] = {}
        for entry in history:
            for tt in entry.get("trip_types", []):
                trip_type_counts[tt] = trip_type_counts.get(tt, 0) + 1
        return {
            "preferred_types": sorted(
                trip_type_counts, key=trip_type_counts.get, reverse=True
            )[:3]
        }

    async def _execute_search(self, filters: SearchFilters) -> List[Dict]:
        """Execute the actual database search query."""
        return await self.db.search_destinations(filters)

    async def _count_results(self, filters: SearchFilters) -> int:
        """Count total matching results."""
        return await self.db.count_destinations(filters)
