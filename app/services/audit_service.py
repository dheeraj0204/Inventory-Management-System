"""Audit Service providing immutable event querying, search, and JSON diff parsing."""

from typing import Any, Dict, List, Optional
from app.database.connection import DatabaseManager, db_manager
from app.models.audit_log import AuditLog
from app.utils.logger import logger


class AuditService:
    """Provides read-only access to system audit logs with filters and diff viewers."""

    def __init__(self, manager: DatabaseManager = db_manager):
        self.manager = manager

    def get_audit_logs(
        self,
        search_query: str = "",
        action_filter: str = "All",
        entity_id: Optional[str] = None,
        limit: int = 200,
    ) -> List[AuditLog]:
        """Queries audit logs with optional search terms, action filter, and entity ID."""
        query = "SELECT * FROM audit_logs WHERE 1=1"
        params: List[Any] = []

        if action_filter and action_filter != "All":
            query += " AND action = ?"
            params.append(action_filter)

        if entity_id:
            query += " AND entity_id = ?"
            params.append(entity_id)

        if search_query:
            cleaned = f"%{search_query.strip().lower()}%"
            query += " AND (LOWER(entity_id) LIKE ? OR LOWER(reason) LIKE ? OR LOWER(old_values) LIKE ? OR LOWER(new_values) LIKE ?)"
            params.extend([cleaned, cleaned, cleaned, cleaned])

        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)

        with self.manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [AuditLog.from_row(r) for r in rows]

    def get_audit_by_id(self, log_id: int) -> Optional[AuditLog]:
        """Fetches a specific audit log entry by ID."""
        with self.manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM audit_logs WHERE id = ?", (log_id,))
            row = cursor.fetchone()
            return AuditLog.from_row(row) if row else None
