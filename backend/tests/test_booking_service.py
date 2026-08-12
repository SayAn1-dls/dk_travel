"""Tests for the booking service."""
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
from app.services.booking_service import (
    BookingService,
    BookingStatus,
    PaymentMethod,
    Booking,
)


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def mock_payment():
    gateway = AsyncMock()
    gateway.charge.return_value = MagicMock(success=True)
    gateway.refund.return_value = MagicMock(success=True)
    return gateway


@pytest.fixture
def booking_service(mock_db, mock_payment):
    return BookingService(mock_db, mock_payment)


@pytest.mark.asyncio
async def test_create_booking_success(booking_service):
    check_in = datetime.utcnow() + timedelta(days=7)
    check_out = check_in + timedelta(days=3)

    booking = await booking_service.create_booking(
        user_id="user123",
        destination_id="dest456",
        check_in=check_in,
        check_out=check_out,
        guests=2,
    )

    assert booking.user_id == "user123"
    assert booking.destination_id == "dest456"
    assert booking.status == BookingStatus.PENDING
    assert booking.guests == 2
    assert booking.total_price > 0


@pytest.mark.asyncio
async def test_create_booking_invalid_dates(booking_service):
    check_in = datetime.utcnow() + timedelta(days=7)
    check_out = check_in - timedelta(days=1)

    with pytest.raises(ValueError, match="Check-in must be before check-out"):
        await booking_service.create_booking(
            user_id="user123",
            destination_id="dest456",
            check_in=check_in,
            check_out=check_out,
        )


@pytest.mark.asyncio
async def test_create_booking_past_date(booking_service):
    check_in = datetime.utcnow() - timedelta(days=1)
    check_out = datetime.utcnow() + timedelta(days=2)

    with pytest.raises(ValueError, match="cannot be in the past"):
        await booking_service.create_booking(
            user_id="user123",
            destination_id="dest456",
            check_in=check_in,
            check_out=check_out,
        )


@pytest.mark.asyncio
async def test_confirm_booking(booking_service):
    check_in = datetime.utcnow() + timedelta(days=7)
    check_out = check_in + timedelta(days=3)

    booking = await booking_service.create_booking(
        user_id="user123",
        destination_id="dest456",
        check_in=check_in,
        check_out=check_out,
    )

    confirmed = await booking_service.confirm_booking(
        booking.id, PaymentMethod.UPI
    )
    assert confirmed.status == BookingStatus.CONFIRMED
    assert confirmed.payment_method == PaymentMethod.UPI


@pytest.mark.asyncio
async def test_cancel_booking_full_refund(booking_service):
    check_in = datetime.utcnow() + timedelta(days=14)
    check_out = check_in + timedelta(days=3)

    booking = await booking_service.create_booking(
        user_id="user123",
        destination_id="dest456",
        check_in=check_in,
        check_out=check_out,
    )
    await booking_service.confirm_booking(booking.id, PaymentMethod.CREDIT_CARD)
    cancelled = await booking_service.cancel_booking(booking.id)

    assert cancelled.status == BookingStatus.REFUNDED


@pytest.mark.asyncio
async def test_get_user_bookings(booking_service):
    check_in = datetime.utcnow() + timedelta(days=7)
    check_out = check_in + timedelta(days=2)

    await booking_service.create_booking(
        user_id="user123",
        destination_id="dest1",
        check_in=check_in,
        check_out=check_out,
    )
    await booking_service.create_booking(
        user_id="user123",
        destination_id="dest2",
        check_in=check_in + timedelta(days=10),
        check_out=check_out + timedelta(days=10),
    )

    bookings = await booking_service.get_user_bookings("user123")
    assert len(bookings) == 2


@pytest.mark.asyncio
async def test_invalid_guest_count(booking_service):
    check_in = datetime.utcnow() + timedelta(days=7)
    check_out = check_in + timedelta(days=2)

    with pytest.raises(ValueError, match="Guests must be between"):
        await booking_service.create_booking(
            user_id="user123",
            destination_id="dest456",
            check_in=check_in,
            check_out=check_out,
            guests=15,
        )
