"""Notification service for travel booking alerts."""
import logging
from enum import Enum
from typing import List, Optional
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


class NotificationType(Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"


class NotificationPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class Notification:
    id: str = ""
    user_id: str = ""
    type: NotificationType = NotificationType.EMAIL
    priority: NotificationPriority = NotificationPriority.MEDIUM
    subject: str = ""
    body: str = ""
    sent: bool = False
    sent_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


class NotificationService:
    """Multi-channel notification delivery service."""

    def __init__(self, email_client, sms_client, push_client):
        self.email = email_client
        self.sms = sms_client
        self.push = push_client
        self._queue: List[Notification] = []

    async def send_booking_confirmation(self, user_id: str, booking_id: str):
        """Send booking confirmation across all channels."""
        notification = Notification(
            user_id=user_id,
            type=NotificationType.EMAIL,
            priority=NotificationPriority.HIGH,
            subject="Booking Confirmed!",
            body=f"Your booking {booking_id} has been confirmed. "
                 f"Check your dashboard for details.",
        )
        await self._dispatch(notification)
        logger.info(f"Booking confirmation sent for {booking_id}")

    async def send_cancellation_notice(self, user_id: str, booking_id: str):
        """Send cancellation notification."""
        notification = Notification(
            user_id=user_id,
            type=NotificationType.EMAIL,
            priority=NotificationPriority.HIGH,
            subject="Booking Cancelled",
            body=f"Your booking {booking_id} has been cancelled. "
                 f"Refund will be processed within 5-7 business days.",
        )
        await self._dispatch(notification)

    async def send_reminder(self, user_id: str, booking_id: str, days_until: int):
        """Send trip reminder notification."""
        notification = Notification(
            user_id=user_id,
            type=NotificationType.PUSH,
            priority=NotificationPriority.MEDIUM,
            subject=f"Trip in {days_until} days!",
            body=f"Your trip is coming up in {days_until} days. "
                 f"Don't forget to pack!",
        )
        await self._dispatch(notification)

    async def _dispatch(self, notification: Notification):
        """Route notification to appropriate channel."""
        handlers = {
            NotificationType.EMAIL: self.email.send,
            NotificationType.SMS: self.sms.send,
            NotificationType.PUSH: self.push.send,
        }
        handler = handlers.get(notification.type)
        if handler:
            try:
                await handler(
                    to=notification.user_id,
                    subject=notification.subject,
                    body=notification.body,
                )
                notification.sent = True
                notification.sent_at = datetime.utcnow()
            except Exception as e:
                logger.error(f"Failed to send notification: {e}")
                self._queue.append(notification)
