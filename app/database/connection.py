"""SQLite Database connection manager with Foreign Key enforcement and transaction control."""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional, Union
from app.config import DEFAULT_DB_PATH
from app.utils.logger import logger


class DatabaseManager:
    """Manages SQLite database connections and transactions."""

    def __init__(self, db_path: Optional[Union[str, Path]] = None):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH

    def get_raw_connection(self) -> sqlite3.Connection:
        """Returns a configured raw SQLite connection with Foreign Keys and Row factory."""
        # Ensure parent directories exist
        if self.db_path != Path(":memory:"):
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(
            str(self.db_path),
            timeout=30.0,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
        )
        conn.row_factory = sqlite3.Row
        # Enforce foreign key constraints
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        return conn

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager for non-transactional or read operations."""
        conn = self.get_raw_connection()
        try:
            yield conn
        finally:
            conn.close()

    @contextmanager
    def transaction(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager providing ACID transaction semantics (Commit on success, Rollback on error)."""
        conn = self.get_raw_connection()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Transaction rollback triggered due to error: {e}", exc_info=True)
            raise
        finally:
            conn.close()


# Default singleton instance
db_manager = DatabaseManager()
