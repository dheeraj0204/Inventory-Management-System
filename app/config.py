"""Application configuration constants and environment paths."""

import os
from pathlib import Path

# Base Paths
APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"

# Ensure runtime directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Database & Log paths
DEFAULT_DB_PATH = DATA_DIR / "inventory_tqm.db"
LOG_FILE_PATH = LOGS_DIR / "app.log"

# Application Metadata
APP_TITLE = "Inventory Management System"
STUDENT_NAME = ""
COURSE_NAME = ""
ACADEMIC_SESSION = "2026–27"
QUALITY_GOAL = "Data Accuracy & Inventory Control"
VERSION = "1.0.0"

# Controlled Dropdown Categories (Q07 Feature 2)
ALLOWED_CATEGORIES = [
    "Electronics",
    "Stationery",
    "Furniture",
    "Accessories",
    "Raw Materials",
    "Other",
]

# Standard Adjustment Reasons
STOCK_ADJUSTMENT_REASONS = [
    "Stock Count Audit Correction",
    "Damaged Goods Write-off",
    "Customer Return Inward",
    "Supplier Restock Inward",
    "Internal Department Issue",
    "Other Correction",
]

# TQM Configuration
DEFECT_CATEGORIES = [
    "Invalid Input",
    "Duplicate Identifier",
    "Incorrect Category",
    "Stock Mismatch",
    "Search Failure",
    "Database Error",
]

DEFECT_SEVERITIES = [
    "Low",
    "Medium",
    "High",
    "Critical",
]

DEFECT_STATUSES = [
    "Open",
    "Under Review",
    "Resolved",
]

PDCA_STAGES = [
    "PLAN",
    "DO",
    "CHECK",
    "ACT",
]

PDCA_STATUSES = [
    "Planned",
    "In Progress",
    "Completed",
    "Needs Revision",
]

# UI Design System Constants
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 800
MIN_WINDOW_WIDTH = 1100
MIN_WINDOW_HEIGHT = 700
