"""Application Entry Point: Desktop Inventory Management System."""

import sys
from app.config import APP_TITLE, VERSION
from app.database import initialize_database
from app.models.user import User
from app.ui.app_window import AppWindow
from app.ui.views.auth_view import AuthWindow
from app.utils.logger import logger


def launch_application():
    """Bootstraps database and manages the login-to-dashboard lifecycle."""
    logger.info(f"Starting {APP_TITLE} v{VERSION}...")

    try:
        # 1. Initialize SQLite Database, tables, constraints, users, and seeds
        initialize_database()
        logger.info("Database schema initialized and verified.")

        def show_dashboard(user: User):
            """Launches main application dashboard for the logged in user."""
            logger.info(f"Launching dashboard session for user: {user.username} ({user.role})")
            app = AppWindow(current_user=user, on_logout=show_login)
            app.mainloop()

        def show_login():
            """Launches modern authentication window (Sign In & Sign Up)."""
            logger.info("Launching access control / authentication window...")
            auth = AuthWindow(on_login_success=show_dashboard)
            auth.mainloop()

        # Start with authentication window
        show_login()

    except Exception as e:
        logger.critical(f"Fatal error during application startup: {e}", exc_info=True)
        sys.exit(1)


def main():
    launch_application()


if __name__ == "__main__":
    main()
