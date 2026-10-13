"""Data model representing an immutable audit log entry."""

from dataclasses import dataclass, asdict
import json
from typing import Any, Dict, Optional
import sqlite3


@dataclass
class AuditLog:
    """Represents an auditable change event in the system."""
    entity_type: str
    entity_id: str
    action: str
    timestamp: str
    old_values: Optional[str] = None  # JSON string
    new_values: Optional[str] = None  # JSON string
    reason: Optional[str] = None
    id: Optional[int] = None

    def get_old_dict(self) -> Dict[str, Any]:
        """Safely parses old_values JSON string into dict."""
        if not self.old_values:
            return {}
        try:
            return json.loads(self.old_values)
        except Exception:
            return {"raw": self.old_values}

    def get_new_dict(self) -> Dict[str, Any]:
        """Safely parses new_values JSON string into dict."""
        if not self.new_values:
            return {}
        try:
            return json.loads(self.new_values)
        except Exception:
            return {"raw": self.new_values}

    def to_dict(self) -> Dict[str, Any]:
        """Converts audit log to dictionary."""
        d = asdict(self)
        d["old_data"] = self.get_old_dict()
        d["new_data"] = self.get_new_dict()
        return d

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "AuditLog":
        """Instantiates AuditLog from SQLite row object."""
        return cls(
            id=row["id"],
            entity_type=row["entity_type"],
            entity_id=row["entity_id"],
            action=row["action"],
            old_values=row["old_values"],
            new_values=row["new_values"],
            reason=row["reason"],
            timestamp=row["timestamp"],
        )
