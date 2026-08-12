"""Authentication service for user management."""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from backend.database import get_database
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class AuthService:
    """Handles user authentication and session management."""

    TOKEN_EXPIRY_HOURS = 24
    MIN_PASSWORD_LENGTH = 8

    def __init__(self):
        self.db = None

    async def _get_users_collection(self):
        if self.db is None:
            self.db = await get_database()
        return self.db["users"]

    async def _get_sessions_collection(self):
        if self.db is None:
            self.db = await get_database()
        return self.db["sessions"]

    @staticmethod
    def _hash_password(password: str, salt: str) -> str:
        """Hash a password with salt using SHA-256."""
        return hashlib.sha256(f"{salt}{password}".encode()).hexdigest()

    @staticmethod
    def _generate_salt() -> str:
        return secrets.token_hex(16)

    @staticmethod
    def _generate_token() -> str:
        return secrets.token_urlsafe(32)

    async def register(
        self,
        email: str,
        password: str,
        full_name: str,
        phone: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Register a new user."""
        if len(password) < self.MIN_PASSWORD_LENGTH:
            raise ValueError(
                f"Password must be at least {self.MIN_PASSWORD_LENGTH} characters"
            )

        users = await self._get_users_collection()
        existing = await users.find_one({"email": email.lower()})
        if existing:
            raise ValueError("Email already registered")

        salt = self._generate_salt()
        hashed = self._hash_password(password, salt)

        user_data = {
            "email": email.lower(),
            "password_hash": hashed,
            "salt": salt,
            "full_name": full_name,
            "phone": phone,
            "is_active": True,
            "is_verified": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        result = await users.insert_one(user_data)
        logger.info(f"User registered: {email}")
        return {
            "user_id": str(result.inserted_id),
            "email": email.lower(),
            "full_name": full_name,
        }

    async def login(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate a user and create a session."""
        users = await self._get_users_collection()
        user = await users.find_one({"email": email.lower(), "is_active": True})

        if not user:
            logger.warning(f"Login attempt for unknown email: {email}")
            return None

        hashed = self._hash_password(password, user["salt"])
        if hashed != user["password_hash"]:
            logger.warning(f"Failed login for: {email}")
            return None

        token = self._generate_token()
        sessions = await self._get_sessions_collection()
        await sessions.insert_one(
            {
                "user_id": str(user["_id"]),
                "token": token,
                "expires_at": datetime.utcnow()
                + timedelta(hours=self.TOKEN_EXPIRY_HOURS),
                "created_at": datetime.utcnow(),
            }
        )

        logger.info(f"User logged in: {email}")
        return {
            "user_id": str(user["_id"]),
            "token": token,
            "expires_at": (
                datetime.utcnow() + timedelta(hours=self.TOKEN_EXPIRY_HOURS)
            ).isoformat(),
        }

    async def validate_token(self, token: str) -> Optional[str]:
        """Validate a session token and return user_id if valid."""
        sessions = await self._get_sessions_collection()
        session = await sessions.find_one(
            {"token": token, "expires_at": {"$gt": datetime.utcnow()}}
        )
        if session:
            return session["user_id"]
        return None

    async def logout(self, token: str) -> bool:
        """Invalidate a session."""
        sessions = await self._get_sessions_collection()
        result = await sessions.delete_one({"token": token})
        return result.deleted_count > 0
