"""Application Entry Point: Desktop Inventory Management System (BBAT104 TQM Q07)."""

import sys
from app.config import APP_TITLE, VERSION, STUDENT_NAME, QUALITY_GOAL
from app.database import initialize_database
from app.ui.app_window import AppWindow
from app.utils.logger import logger


def main():
    """Bootstraps the database and launches the CustomTkinter desktop interface."""
    logger.info(f"Starting {APP_TITLE} v{VERSION}...")
    logger.info(f"Student: {STUDENT_NAME} • Goal: {QUALITY_GOAL}")

    try:
        # 1. Initialize SQLite Database, tables, constraints, and initial seed
        initialize_database()
        logger.info("Database schema initialized and verified.")

        # 2. Launch Desktop GUI Window
        app = AppWindow()
        logger.info("Main application window initialized successfully.")
        app.mainloop()

    except Exception as e:
        logger.critical(f"Fatal error during application startup: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
