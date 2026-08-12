"""Unit tests for AuthService."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from bson import ObjectId

from backend.services.auth_service import AuthService


class TestAuthService:
    """Tests for the AuthService class."""

    def setup_method(self):
        self.service = AuthService()

    def test_hash_password_consistency(self):
        """Same password + salt should produce same hash."""
        salt = "test-salt-123"
        hash1 = self.service._hash_password("mypassword", salt)
        hash2 = self.service._hash_password("mypassword", salt)
        assert hash1 == hash2

    def test_hash_password_different_salts(self):
        """Different salts should produce different hashes."""
        hash1 = self.service._hash_password("mypassword", "salt1")
        hash2 = self.service._hash_password("mypassword", "salt2")
        assert hash1 != hash2

    def test_generate_salt_uniqueness(self):
        """Generated salts should be unique."""
        salt1 = self.service._generate_salt()
        salt2 = self.service._generate_salt()
        assert salt1 != salt2
        assert len(salt1) == 32  # 16 bytes = 32 hex chars

    def test_generate_token_length(self):
        """Generated tokens should have reasonable length."""
        token = self.service._generate_token()
        assert len(token) > 20

    @pytest.mark.asyncio
    async def test_register_short_password(self):
        """Should reject passwords shorter than minimum length."""
        with pytest.raises(ValueError, match="Password must be at least"):
            await self.service.register(
                email="test@example.com",
                password="short",
                full_name="Test User",
            )

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self):
        """Should reject registration with existing email."""
        mock_collection = AsyncMock()
        mock_collection.find_one = AsyncMock(
            return_value={"_id": ObjectId(), "email": "test@example.com"}
        )

        with patch.object(
            self.service, '_get_users_collection', return_value=mock_collection
        ):
            with pytest.raises(ValueError, match="Email already registered"):
                await self.service.register(
                    email="test@example.com",
                    password="ValidPass123",
                    full_name="Test User",
                )

    @pytest.mark.asyncio
    async def test_login_invalid_email(self):
        """Should return None for non-existent email."""
        mock_collection = AsyncMock()
        mock_collection.find_one = AsyncMock(return_value=None)

        with patch.object(
            self.service, '_get_users_collection', return_value=mock_collection
        ):
            result = await self.service.login("unknown@example.com", "password")
            assert result is None

    @pytest.mark.asyncio
    async def test_validate_token_expired(self):
        """Should return None for expired token."""
        mock_collection = AsyncMock()
        mock_collection.find_one = AsyncMock(return_value=None)

        with patch.object(
            self.service, '_get_sessions_collection', return_value=mock_collection
        ):
            result = await self.service.validate_token("expired-token")
            assert result is None
