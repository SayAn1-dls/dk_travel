"""Destination API routes."""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from backend.services.search_service import SearchService

router = APIRouter()
search_service = SearchService()


@router.get("/")
async def list_destinations(
    q: Optional[str] = Query(None, description="Search query"),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    min_rating: Optional[float] = Query(None, ge=0, le=5),
    country: Optional[str] = None,
    sort_by: str = Query("rating", enum=["price", "rating", "name"]),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """Search and list travel destinations."""
    results = await search_service.search_destinations(
        query=q,
        category=category,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
        country=country,
        sort_by=sort_by,
        page=page,
        page_size=page_size,
    )
    return results


@router.get("/popular")
async def popular_destinations(limit: int = Query(10, ge=1, le=50)):
    """Get the most popular destinations."""
    return await search_service.get_popular_destinations(limit=limit)


@router.get("/categories")
async def list_categories():
    """Get all available destination categories."""
    categories = await search_service.get_categories()
    return {"categories": categories}


@router.get("/{destination_id}")
async def get_destination(destination_id: str):
    """Get details for a specific destination."""
    dest = await search_service.get_destination(destination_id)
    if not dest:
        raise HTTPException(status_code=404, detail="Destination not found")
    return dest
