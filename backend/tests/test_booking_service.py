"""Unit tests for BookingService."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch, MagicMock
from bson import ObjectId

from backend.services.booking_service import BookingService


class TestBookingService:
    """Tests for the BookingService class."""

    def setup_method(self):
        self.service = BookingService()

    @pytest.mark.asyncio
    async def test_create_booking_invalid_dates(self):
        """Should raise ValueError when check-out is before check-in."""
        check_in = datetime.utcnow() + timedelta(days=5)
        check_out = datetime.utcnow() + timedelta(days=2)

        with pytest.raises(ValueError, match="Check-out date must be after check-in"):
            await self.service.create_booking(
                user_id="user-1",
                destination_id="dest-1",
                check_in=check_in,
                check_out=check_out,
            )

    @pytest.mark.asyncio
    async def test_create_booking_invalid_guests(self):
        """Should raise ValueError for invalid guest count."""
        check_in = datetime.utcnow() + timedelta(days=1)
        check_out = datetime.utcnow() + timedelta(days=3)

        with pytest.raises(ValueError, match="Guest count must be between"):
            await self.service.create_booking(
                user_id="user-1",
                destination_id="dest-1",
                check_in=check_in,
                check_out=check_out,
                guests=15,
            )

    @pytest.mark.asyncio
    async def test_create_booking_success(self, mock_db):
        """Should create a booking successfully with valid data."""
        mock_collection = AsyncMock()
        mock_collection.insert_one = AsyncMock(
            return_value=MagicMock(inserted_id=ObjectId())
        )

        with patch.object(self.service, '_get_collection', return_value=mock_collection):
            check_in = datetime.utcnow() + timedelta(days=1)
            check_out = datetime.utcnow() + timedelta(days=4)

            result = await self.service.create_booking(
                user_id="user-1",
                destination_id="dest-1",
                check_in=check_in,
                check_out=check_out,
                guests=2,
                special_requests="Early check-in",
            )

            assert result is not None
            assert result["user_id"] == "user-1"
            assert result["guests"] == 2
            assert result["nights"] == 3
            mock_collection.insert_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_booking_not_found(self):
        """Should return None when booking doesn't exist."""
        mock_collection = AsyncMock()
        mock_collection.find_one = AsyncMock(return_value=None)

        with patch.object(self.service, '_get_collection', return_value=mock_collection):
            result = await self.service.get_booking(str(ObjectId()))
            assert result is None
