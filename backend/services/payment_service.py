"""Payment service for handling transactions."""

import hashlib
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

from backend.database import get_database
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class PaymentStatus(str, Enum):
    INITIATED = "initiated"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentService:
    """Handles payment processing for bookings."""

    SUPPORTED_METHODS = ["credit_card", "debit_card", "upi", "net_banking", "wallet"]

    def __init__(self):
        self.db = None
        self.collection_name = "payments"

    async def _get_collection(self):
        if self.db is None:
            self.db = await get_database()
        return self.db[self.collection_name]

    def _generate_transaction_id(self) -> str:
        """Generate a unique transaction ID."""
        unique = f"{uuid.uuid4()}-{datetime.utcnow().timestamp()}"
        return f"TXN-{hashlib.sha256(unique.encode()).hexdigest()[:12].upper()}"

    async def initiate_payment(
        self,
        booking_id: str,
        user_id: str,
        amount: float,
        currency: str = "INR",
        method: str = "credit_card",
    ) -> Dict[str, Any]:
        """Initiate a payment for a booking."""
        if method not in self.SUPPORTED_METHODS:
            raise ValueError(f"Unsupported payment method: {method}")
        if amount <= 0:
            raise ValueError("Amount must be positive")

        collection = await self._get_collection()
        transaction_id = self._generate_transaction_id()

        payment_data = {
            "transaction_id": transaction_id,
            "booking_id": booking_id,
            "user_id": user_id,
            "amount": amount,
            "currency": currency,
            "method": method,
            "status": PaymentStatus.INITIATED.value,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        result = await collection.insert_one(payment_data)
        payment_data["_id"] = str(result.inserted_id)
        logger.info(f"Payment initiated: {transaction_id} for booking {booking_id}")
        return payment_data

    async def process_payment(self, transaction_id: str) -> Dict[str, Any]:
        """Process an initiated payment (mock gateway call)."""
        collection = await self._get_collection()
        payment = await collection.find_one({"transaction_id": transaction_id})

        if not payment:
            raise ValueError(f"Payment not found: {transaction_id}")
        if payment["status"] != PaymentStatus.INITIATED.value:
            raise ValueError(f"Payment cannot be processed in state: {payment['status']}")

        # Simulate gateway processing
        await collection.update_one(
            {"transaction_id": transaction_id},
            {
                "$set": {
                    "status": PaymentStatus.COMPLETED.value,
                    "processed_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                    "gateway_response": {"code": "SUCCESS", "message": "Payment processed"},
                }
            },
        )

        logger.info(f"Payment completed: {transaction_id}")
        return {"transaction_id": transaction_id, "status": PaymentStatus.COMPLETED.value}

    async def refund_payment(
        self, transaction_id: str, reason: str = ""
    ) -> Dict[str, Any]:
        """Refund a completed payment."""
        collection = await self._get_collection()
        result = await collection.update_one(
            {"transaction_id": transaction_id, "status": PaymentStatus.COMPLETED.value},
            {
                "$set": {
                    "status": PaymentStatus.REFUNDED.value,
                    "refund_reason": reason,
                    "refunded_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                }
            },
        )
        if result.modified_count > 0:
            logger.info(f"Payment refunded: {transaction_id}")
            return {"transaction_id": transaction_id, "status": PaymentStatus.REFUNDED.value}
        raise ValueError("Cannot refund: payment not found or not in completed state")

    async def get_payment_status(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """Get the current status of a payment."""
        collection = await self._get_collection()
        payment = await collection.find_one(
            {"transaction_id": transaction_id},
            {"_id": 0, "transaction_id": 1, "status": 1, "amount": 1, "currency": 1},
        )
        return payment
