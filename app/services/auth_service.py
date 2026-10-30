"""Authentication and user management service with secure PBKDF2 hashing and session control."""

from datetime import datetime, timezone
import hashlib
import hmac
import re
import secrets
from typing import List, Optional, Tuple

from app.database.connection import DatabaseManager, db_manager
from app.models.user import User
from app.utils.logger import logger
from app.utils.validators import ValidationError


class AuthService:
    """Service managing user authentication, registration, password hashing, and active session."""

    def __init__(self, manager: DatabaseManager = db_manager):
        self.manager = manager
        self._current_user: Optional[User] = None

    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """Derives a secure 256-bit PBKDF2 key with 100,000 iterations of SHA-256."""
        if not salt:
            salt = secrets.token_hex(16)
        key = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            100000,
        )
        return key.hex(), salt

    @staticmethod
    def verify_password(password: str, salt: str, password_hash: str) -> bool:
        """Verifies password candidate against stored hash using constant-time comparison."""
        key = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            100000,
        )
        return hmac.compare_digest(key.hex(), password_hash)

    def authenticate(self, username: str, password: str) -> Tuple[bool, str, Optional[User]]:
        """Authenticates user against SQLite database credentials."""
        clean_user = username.strip()
        if not clean_user or not password:
            return False, "Username and password are required.", None

        with self.manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE username = ? COLLATE NOCASE",
                (clean_user,),
            )
            row = cursor.fetchone()

            if not row:
                return False, "Invalid username or password.", None

            is_valid = self.verify_password(password, row["salt"], row["password_hash"])
            if not is_valid:
                return False, "Invalid username or password.", None

            user = User.from_row(row)

        # Update last login timestamp
        now_ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        try:
            with self.manager.transaction() as conn:
                conn.execute(
                    "UPDATE users SET last_login = ? WHERE id = ?",
                    (now_ts, user.id),
                )
                # Audit log entry for login
                conn.execute(
                    """
                    INSERT INTO audit_logs (entity_type, entity_id, action, old_values, new_values, reason, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    ("USER", user.username, "UPDATE", None, None, f"User '{user.username}' logged in successfully", now_ts),
                )
        except Exception as e:
            logger.warning(f"Could not update last_login timestamp: {e}")

        user.last_login = now_ts
        self._current_user = user
        logger.info(f"User '{user.username}' ({user.role}) authenticated successfully.")
        return True, "Login successful.", user

    def register_user(
        self,
        username: str,
        password: str,
        full_name: str,
        email: Optional[str] = None,
        role: str = "Staff",
    ) -> Tuple[bool, str, Optional[User]]:
        """Registers a new user into SQLite with validation, password hashing, and audit logging."""
        clean_username = username.strip()
        clean_full_name = full_name.strip()
        clean_email = email.strip() if email else None
        clean_role = role.strip() if role else "Staff"

        # 1. Validation checks
        if not clean_username:
            return False, "Username is required.", None
        if len(clean_username) < 3 or len(clean_username) > 30:
            return False, "Username must be between 3 and 30 characters.", None
        if not re.match(r"^[a-zA-Z0-9_.-]+$", clean_username):
            return False, "Username may only contain letters, numbers, hyphens, and underscores.", None

        if not clean_full_name or len(clean_full_name) < 2:
            return False, "Full Name must be at least 2 characters.", None

        if not password or len(password) < 6:
            return False, "Password must be at least 6 characters long.", None

        if clean_email:
            email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
            if not re.match(email_pattern, clean_email):
                return False, "Invalid email address format.", None

        allowed_roles = ("Admin", "Manager", "Staff")
        if clean_role not in allowed_roles:
            clean_role = "Staff"

        # 2. Uniqueness verification
        with self.manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM users WHERE username = ? COLLATE NOCASE",
                (clean_username,),
            )
            if cursor.fetchone():
                return False, f"Username '{clean_username}' is already taken. Please choose another.", None

            if clean_email:
                cursor.execute(
                    "SELECT 1 FROM users WHERE email = ? COLLATE NOCASE",
                    (clean_email,),
                )
                if cursor.fetchone():
                    return False, f"Email '{clean_email}' is already registered with another account.", None

        # 3. Hash password and insert
        pwd_hash, salt = self.hash_password(password)
        now_ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        with self.manager.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO users (username, password_hash, salt, full_name, email, role, created_at, last_login)
                VALUES (?, ?, ?, ?, ?, ?, ?, NULL)
                """,
                (clean_username, pwd_hash, salt, clean_full_name, clean_email, clean_role, now_ts),
            )
            user_id = cursor.lastrowid

            # Audit record
            conn.execute(
                """
                INSERT INTO audit_logs (entity_type, entity_id, action, old_values, new_values, reason, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "USER",
                    clean_username,
                    "CREATE",
                    None,
                    f'{{"username": "{clean_username}", "role": "{clean_role}", "full_name": "{clean_full_name}"}}',
                    f"New user registered: {clean_username} ({clean_role})",
                    now_ts,
                ),
            )

        new_user = User(
            id=user_id,
            username=clean_username,
            full_name=clean_full_name,
            role=clean_role,
            email=clean_email,
            created_at=now_ts,
            last_login=None,
        )
        logger.info(f"New user account registered: {clean_username} ({clean_role})")
        return True, "Account registered successfully! You can now log in.", new_user

    def get_current_user(self) -> Optional[User]:
        """Returns the currently authenticated user in session."""
        return self._current_user

    def set_current_user(self, user: Optional[User]) -> None:
        """Sets active session user."""
        self._current_user = user

    def logout(self) -> None:
        """Terminates active session and records logout audit log."""
        if self._current_user:
            now_ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            try:
                with self.manager.transaction() as conn:
                    conn.execute(
                        """
                        INSERT INTO audit_logs (entity_type, entity_id, action, old_values, new_values, reason, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        ("USER", self._current_user.username, "UPDATE", None, None, f"User '{self._current_user.username}' logged out", now_ts),
                    )
            except Exception as e:
                logger.warning(f"Could not log logout event: {e}")
            logger.info(f"User '{self._current_user.username}' logged out.")
        self._current_user = None

    def get_all_users(self) -> List[User]:
        """Retrieves list of all registered users."""
        with self.manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users ORDER BY username ASC")
            return [User.from_row(r) for r in cursor.fetchall()]


# Singleton instance
auth_service = AuthService()
