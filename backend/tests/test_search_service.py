"""Tests for the search and filter service."""
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.search_service import (
    SearchService,
    SearchFilters,
    SortBy,
    TripType,
)


@pytest.fixture
def mock_db():
    db = AsyncMock()
    db.search_destinations.return_value = [
        {"id": "1", "name": "Manali", "rating": 4.5, "price": 3000},
        {"id": "2", "name": "Goa", "rating": 4.3, "price": 4500},
    ]
    db.count_destinations.return_value = 2
    db.find_matching.return_value = ["Manali", "Mangalore", "Mandarmani"]
    db.get_trending_destinations.return_value = [
        {"id": "1", "name": "Manali", "searches": 1500},
    ]
    return db


@pytest.fixture
def search_service(mock_db):
    return SearchService(mock_db)


@pytest.mark.asyncio
async def test_search_basic(search_service):
    filters = SearchFilters(query="Manali")
    result = await search_service.search(filters)

    assert "results" in result
    assert "total" in result
    assert result["total"] == 2
    assert result["page"] == 1


@pytest.mark.asyncio
async def test_search_with_price_filter(search_service):
    filters = SearchFilters(
        query="beach",
        min_price=2000,
        max_price=5000,
    )
    result = await search_service.search(filters)
    assert "results" in result
    assert "filters_applied" in result


@pytest.mark.asyncio
async def test_search_with_sorting(search_service):
    filters = SearchFilters(
        query="mountain",
        sort_by=SortBy.RATING,
    )
    result = await search_service.search(filters)
    assert result["filters_applied"]["sort_by"] == "rating"


@pytest.mark.asyncio
async def test_autocomplete(search_service):
    suggestions = await search_service.autocomplete("Man")
    assert len(suggestions) == 3
    assert "Manali" in suggestions


@pytest.mark.asyncio
async def test_autocomplete_short_query(search_service):
    suggestions = await search_service.autocomplete("M")
    assert len(suggestions) == 0


@pytest.mark.asyncio
async def test_get_trending(search_service):
    trending = await search_service.get_trending(limit=5)
    assert len(trending) > 0
    assert trending[0]["name"] == "Manali"


@pytest.mark.asyncio
async def test_search_with_cache(mock_db):
    cache = AsyncMock()
    cache.get.return_value = None
    service = SearchService(mock_db, cache_client=cache)

    filters = SearchFilters(query="test")
    await service.search(filters)

    cache.get.assert_called_once()
    cache.set.assert_called_once()


@pytest.mark.asyncio
async def test_search_cache_hit(mock_db):
    cached_result = {"results": [], "total": 0, "page": 1}
    cache = AsyncMock()
    cache.get.return_value = cached_result
    service = SearchService(mock_db, cache_client=cache)

    filters = SearchFilters(query="test")
    result = await service.search(filters)

    assert result == cached_result
    mock_db.search_destinations.assert_not_called()


@pytest.mark.asyncio
async def test_pagination(search_service):
    filters = SearchFilters(query="all", page=2, per_page=10)
    result = await search_service.search(filters)

    assert result["page"] == 2
    assert result["per_page"] == 10
