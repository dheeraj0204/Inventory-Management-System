"""Automated test suite verifying user authentication, registration, hashing, and session management."""

import pytest
from app.services.auth_service import AuthService


class TestAuthService:
    """Tests for AuthService operations and security constraints."""

    def test_preseeded_admin_user_authenticates(self, test_auth_service: AuthService):
        """Verifies that default seed admin account can log in."""
        success, msg, user = test_auth_service.authenticate("admin", "admin123")
        assert success is True
        assert user is not None
        assert user.username == "admin"
        assert user.role == "Admin"
        assert test_auth_service.get_current_user() == user

    def test_invalid_password_rejected(self, test_auth_service: AuthService):
        """Verifies incorrect password attempt is rejected."""
        success, msg, user = test_auth_service.authenticate("admin", "wrong_pass")
        assert success is False
        assert user is None
        assert "Invalid username or password" in msg

    def test_nonexistent_user_rejected(self, test_auth_service: AuthService):
        """Verifies unknown username is rejected."""
        success, msg, user = test_auth_service.authenticate("ghost_user", "some_pass")
        assert success is False
        assert user is None

    def test_register_new_user_success(self, test_auth_service: AuthService):
        """Verifies successful registration of a new user account."""
        success, msg, new_user = test_auth_service.register_user(
            username="rohit_sharma",
            password="SecurePassword123",
            full_name="Rohit Sharma",
            email="rohit@inventory.local",
            role="Manager",
        )
        assert success is True
        assert new_user is not None
        assert new_user.username == "rohit_sharma"
        assert new_user.role == "Manager"

        # Now authenticate with the new account
        auth_ok, auth_msg, authed = test_auth_service.authenticate("rohit_sharma", "SecurePassword123")
        assert auth_ok is True
        assert authed.full_name == "Rohit Sharma"

    def test_duplicate_username_rejected(self, test_auth_service: AuthService):
        """Verifies that duplicate usernames cannot be created."""
        success, msg, _ = test_auth_service.register_user(
            username="admin",  # Already seeded
            password="Password123",
            full_name="Duplicate Admin",
        )
        assert success is False
        assert "already taken" in msg.lower()

    def test_short_password_rejected(self, test_auth_service: AuthService):
        """Verifies password length constraint enforcement."""
        success, msg, _ = test_auth_service.register_user(
            username="new_user_short",
            password="123",  # Less than 6 chars
            full_name="Short Pwd User",
        )
        assert success is False
        assert "at least 6 characters" in msg

    def test_logout_terminates_session(self, test_auth_service: AuthService):
        """Verifies session termination upon logout."""
        test_auth_service.authenticate("admin", "admin123")
        assert test_auth_service.get_current_user() is not None

        test_auth_service.logout()
        assert test_auth_service.get_current_user() is None
