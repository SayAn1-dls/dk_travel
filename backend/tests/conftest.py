"""Shared test fixtures for the DK Travel backend."""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_db():
    """Create a mock database for testing."""
    db = MagicMock()
    db.__getitem__ = MagicMock(return_value=AsyncMock())
    return db


@pytest.fixture
def sample_destination():
    """Sample destination data for tests."""
    return {
        "name": "Goa Beach Resort",
        "country": "India",
        "category": "Beach",
        "description": "A beautiful beachside resort in Goa.",
        "price_per_night": 5000,
        "rating": 4.5,
        "image_url": "https://example.com/goa.jpg",
        "is_active": True,
    }


@pytest.fixture
def sample_user():
    """Sample user data for tests."""
    return {
        "email": "test@example.com",
        "password": "TestPass123",
        "full_name": "Test User",
        "phone": "+919876543210",
    }


@pytest.fixture
def sample_booking():
    """Sample booking data for tests."""
    return {
        "user_id": "test-user-id",
        "destination_id": "test-dest-id",
        "check_in": "2026-09-01T00:00:00",
        "check_out": "2026-09-05T00:00:00",
        "guests": 2,
        "special_requests": "Late check-in please",
    }
