"""Centralized logging setup for the Inventory TQM application."""

import logging
import sys
from app.config import LOG_FILE_PATH

_logger_initialized = False


def setup_logger(name: str = "inventory_tqm") -> logging.Logger:
    """Configures and returns the application logger."""
    global _logger_initialized
    logger = logging.getLogger(name)

    if not _logger_initialized:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s:%(funcName)s:%(lineno)d] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # File Handler
        file_handler = logging.FileHandler(LOG_FILE_PATH, encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        _logger_initialized = True

    return logger


logger = setup_logger()
