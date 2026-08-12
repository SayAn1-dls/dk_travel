"""Booking service for managing travel reservations."""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from bson import ObjectId

from backend.database import get_database
from backend.models.booking import Booking, BookingStatus
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class BookingService:
    """Handles all booking-related business logic."""

    def __init__(self):
        self.db = None
        self.collection_name = "bookings"

    async def _get_collection(self):
        if self.db is None:
            self.db = await get_database()
        return self.db[self.collection_name]

    async def create_booking(
        self,
        user_id: str,
        destination_id: str,
        check_in: datetime,
        check_out: datetime,
        guests: int = 1,
        special_requests: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new travel booking."""
        if check_out <= check_in:
            raise ValueError("Check-out date must be after check-in date")
        if guests < 1 or guests > 10:
            raise ValueError("Guest count must be between 1 and 10")

        nights = (check_out - check_in).days
        collection = await self._get_collection()

        booking_data = {
            "user_id": user_id,
            "destination_id": destination_id,
            "check_in": check_in,
            "check_out": check_out,
            "nights": nights,
            "guests": guests,
            "special_requests": special_requests,
            "status": BookingStatus.PENDING.value,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        result = await collection.insert_one(booking_data)
        booking_data["_id"] = str(result.inserted_id)
        logger.info(f"Booking created: {result.inserted_id}")
        return booking_data

    async def get_booking(self, booking_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a booking by ID."""
        collection = await self._get_collection()
        booking = await collection.find_one({"_id": ObjectId(booking_id)})
        if booking:
            booking["_id"] = str(booking["_id"])
        return booking

    async def get_user_bookings(
        self, user_id: str, status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get all bookings for a user, optionally filtered by status."""
        collection = await self._get_collection()
        query = {"user_id": user_id}
        if status:
            query["status"] = status

        cursor = collection.find(query).sort("created_at", -1)
        bookings = await cursor.to_list(length=100)
        for b in bookings:
            b["_id"] = str(b["_id"])
        return bookings

    async def cancel_booking(self, booking_id: str, reason: str = "") -> bool:
        """Cancel an existing booking."""
        collection = await self._get_collection()
        result = await collection.update_one(
            {"_id": ObjectId(booking_id), "status": BookingStatus.PENDING.value},
            {
                "$set": {
                    "status": BookingStatus.CANCELLED.value,
                    "cancellation_reason": reason,
                    "cancelled_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                }
            },
        )
        if result.modified_count > 0:
            logger.info(f"Booking cancelled: {booking_id}")
            return True
        return False

    async def confirm_booking(self, booking_id: str, payment_id: str) -> bool:
        """Confirm a booking after payment."""
        collection = await self._get_collection()
        result = await collection.update_one(
            {"_id": ObjectId(booking_id), "status": BookingStatus.PENDING.value},
            {
                "$set": {
                    "status": BookingStatus.CONFIRMED.value,
                    "payment_id": payment_id,
                    "confirmed_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                }
            },
        )
        return result.modified_count > 0
