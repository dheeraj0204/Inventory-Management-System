"""Data model representing an application user."""

from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional
import sqlite3


@dataclass
class User:
    """Represents an authenticated system user with role-based access."""
    username: str
    full_name: str
    role: str = "Manager"  # Admin, Manager, Staff
    email: Optional[str] = None
    created_at: Optional[str] = None
    last_login: Optional[str] = None
    id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Converts user instance to dictionary without sensitive fields."""
        d = asdict(self)
        return d

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "User":
        """Instantiates User from SQLite row object."""
        return cls(
            id=row["id"] if "id" in row.keys() else None,
            username=row["username"],
            full_name=row["full_name"],
            role=row["role"],
            email=row["email"] if "email" in row.keys() else None,
            created_at=row["created_at"] if "created_at" in row.keys() else None,
            last_login=row["last_login"] if "last_login" in row.keys() else None,
        )
