"""Booking service for managing travel reservations."""
import uuid
from datetime import datetime, timedelta
from typing import Optional, List
from dataclasses import dataclass, field
from enum import Enum


class BookingStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    REFUNDED = "refunded"


class PaymentMethod(Enum):
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    UPI = "upi"
    NET_BANKING = "net_banking"
    WALLET = "wallet"


@dataclass
class Booking:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    destination_id: str = ""
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None
    guests: int = 1
    total_price: float = 0.0
    currency: str = "INR"
    status: BookingStatus = BookingStatus.PENDING
    payment_method: Optional[PaymentMethod] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    notes: str = ""


class BookingService:
    """Handles booking CRUD and payment processing."""

    def __init__(self, db_session, payment_gateway):
        self.db = db_session
        self.payment = payment_gateway
        self._bookings: dict = {}

    async def create_booking(
        self,
        user_id: str,
        destination_id: str,
        check_in: datetime,
        check_out: datetime,
        guests: int = 1,
        notes: str = "",
    ) -> Booking:
        """Create a new booking."""
        if check_in >= check_out:
            raise ValueError("Check-in must be before check-out")
        if check_in < datetime.utcnow():
            raise ValueError("Check-in date cannot be in the past")
        if guests < 1 or guests > 10:
            raise ValueError("Guests must be between 1 and 10")

        nights = (check_out - check_in).days
        price_per_night = await self._get_price(destination_id, guests)
        total = nights * price_per_night

        booking = Booking(
            user_id=user_id,
            destination_id=destination_id,
            check_in=check_in,
            check_out=check_out,
            guests=guests,
            total_price=total,
            notes=notes,
        )

        self._bookings[booking.id] = booking
        return booking

    async def confirm_booking(
        self, booking_id: str, payment_method: PaymentMethod
    ) -> Booking:
        """Confirm and process payment for a booking."""
        booking = self._bookings.get(booking_id)
        if not booking:
            raise ValueError(f"Booking {booking_id} not found")
        if booking.status != BookingStatus.PENDING:
            raise ValueError(f"Booking is {booking.status.value}, cannot confirm")

        payment_result = await self.payment.charge(
            amount=booking.total_price,
            currency=booking.currency,
            method=payment_method,
        )

        if payment_result.success:
            booking.status = BookingStatus.CONFIRMED
            booking.payment_method = payment_method
            booking.updated_at = datetime.utcnow()
        else:
            raise RuntimeError(f"Payment failed: {payment_result.error}")

        return booking

    async def cancel_booking(self, booking_id: str) -> Booking:
        """Cancel a booking and process refund if applicable."""
        booking = self._bookings.get(booking_id)
        if not booking:
            raise ValueError(f"Booking {booking_id} not found")

        if booking.status == BookingStatus.CONFIRMED:
            days_until = (booking.check_in - datetime.utcnow()).days
            refund_pct = 1.0 if days_until > 7 else 0.5 if days_until > 2 else 0.0
            if refund_pct > 0:
                await self.payment.refund(
                    amount=booking.total_price * refund_pct,
                    currency=booking.currency,
                )
                if refund_pct == 1.0:
                    booking.status = BookingStatus.REFUNDED
                else:
                    booking.status = BookingStatus.CANCELLED
        else:
            booking.status = BookingStatus.CANCELLED

        booking.updated_at = datetime.utcnow()
        return booking

    async def get_user_bookings(
        self, user_id: str, status: Optional[BookingStatus] = None
    ) -> List[Booking]:
        """Get all bookings for a user."""
        bookings = [
            b for b in self._bookings.values() if b.user_id == user_id
        ]
        if status:
            bookings = [b for b in bookings if b.status == status]
        return sorted(bookings, key=lambda b: b.created_at, reverse=True)

    async def _get_price(self, destination_id: str, guests: int) -> float:
        """Calculate price per night based on destination and guests."""
        base_price = 2500.0
        return base_price * (1 + (guests - 1) * 0.3)
