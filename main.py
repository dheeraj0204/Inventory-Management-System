"""Application Entry Point: Desktop and Web Inventory Management System."""

import os
import sys
from app.config import APP_TITLE, VERSION
from app.database import initialize_database
from app.utils.logger import logger


def run_web_server():
    """Runs the modern animated web server interface."""
    from web_app import create_app
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"Starting {APP_TITLE} Web Server on port {port}...")
    app = create_app()
    app.run(host="0.0.0.0", port=port, debug=False)


def launch_application():
    """Bootstraps database and manages the login-to-dashboard lifecycle."""
    # Check if we are running in web mode (Embarko or explicit flag)
    if "PORT" in os.environ or "--web" in sys.argv:
        run_web_server()
        return

    logger.info(f"Starting {APP_TITLE} v{VERSION}...")

    try:
        # Initialize SQLite Database, tables, constraints, users, and seeds
        initialize_database()
        logger.info("Database schema initialized and verified.")

        from app.models.user import User
        from app.ui.app_window import AppWindow
        from app.ui.views.auth_view import AuthWindow

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
        # Fall back to web server if GUI/Display is not available (e.g. headless cloud container)
        err_msg = str(e).lower()
        if "display" in err_msg or "tcl" in err_msg or "tkinter" in err_msg:
            logger.warning(f"GUI display not available ({e}). Launching Web Server fallback...")
            run_web_server()
        else:
            logger.critical(f"Fatal error during application startup: {e}", exc_info=True)
            sys.exit(1)


def main():
    launch_application()


if __name__ == "__main__":
    main()
