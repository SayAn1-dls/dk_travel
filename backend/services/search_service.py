"""Search service for finding travel destinations."""

from typing import Optional, Dict, Any, List
from datetime import datetime

from backend.database import get_database
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class SearchService:
    """Handles destination search and filtering logic."""

    VALID_SORT_FIELDS = ["price", "rating", "name", "created_at"]
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100

    def __init__(self):
        self.db = None
        self.collection_name = "destinations"

    async def _get_collection(self):
        if self.db is None:
            self.db = await get_database()
        return self.db[self.collection_name]

    async def search_destinations(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_rating: Optional[float] = None,
        country: Optional[str] = None,
        sort_by: str = "rating",
        sort_order: int = -1,
        page: int = 1,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> Dict[str, Any]:
        """Search destinations with flexible filters."""
        collection = await self._get_collection()
        filters: Dict[str, Any] = {"is_active": True}

        if query:
            filters["$text"] = {"$search": query}
        if category:
            filters["category"] = category
        if country:
            filters["country"] = {"$regex": country, "$options": "i"}
        if min_price is not None or max_price is not None:
            price_filter = {}
            if min_price is not None:
                price_filter["$gte"] = min_price
            if max_price is not None:
                price_filter["$lte"] = max_price
            filters["price_per_night"] = price_filter
        if min_rating is not None:
            filters["rating"] = {"$gte": min_rating}

        if sort_by not in self.VALID_SORT_FIELDS:
            sort_by = "rating"
        page_size = min(page_size, self.MAX_PAGE_SIZE)
        skip = (page - 1) * page_size

        total = await collection.count_documents(filters)
        cursor = (
            collection.find(filters)
            .sort(sort_by, sort_order)
            .skip(skip)
            .limit(page_size)
        )
        results = await cursor.to_list(length=page_size)

        for r in results:
            r["_id"] = str(r["_id"])

        logger.info(f"Search returned {len(results)} of {total} results")

        return {
            "results": results,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

    async def get_destination(self, destination_id: str) -> Optional[Dict[str, Any]]:
        """Get a single destination by ID."""
        from bson import ObjectId
        collection = await self._get_collection()
        dest = await collection.find_one({"_id": ObjectId(destination_id)})
        if dest:
            dest["_id"] = str(dest["_id"])
        return dest

    async def get_popular_destinations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Return top-rated destinations."""
        collection = await self._get_collection()
        cursor = (
            collection.find({"is_active": True})
            .sort("rating", -1)
            .limit(limit)
        )
        results = await cursor.to_list(length=limit)
        for r in results:
            r["_id"] = str(r["_id"])
        return results

    async def get_categories(self) -> List[str]:
        """List all available destination categories."""
        collection = await self._get_collection()
        categories = await collection.distinct("category", {"is_active": True})
        return sorted(categories)
