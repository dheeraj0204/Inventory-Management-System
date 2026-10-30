"""Database schema definitions, tables initialization, and safe seed migrations."""

import json
from datetime import datetime, timezone
import sqlite3
from app.database.connection import DatabaseManager, db_manager
from app.utils.logger import logger


SCHEMA_SQL = """
-- 1. Products Table
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    sku TEXT NOT NULL UNIQUE,
    quantity INTEGER NOT NULL CHECK (quantity >= 0),
    unit_price REAL NOT NULL CHECK (unit_price > 0),
    reorder_level INTEGER NOT NULL DEFAULT 5 CHECK (reorder_level >= 0),
    supplier_name TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Indexes for lightning fast searching and integrity checks
CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku);
CREATE INDEX IF NOT EXISTS idx_products_name ON products(name);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);

-- 2. Stock Movements Table
CREATE TABLE IF NOT EXISTS stock_movements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id TEXT NOT NULL,
    movement_type TEXT NOT NULL CHECK (movement_type IN ('IN', 'OUT', 'ADJUSTMENT', 'INITIAL')),
    quantity_change INTEGER NOT NULL,
    previous_quantity INTEGER NOT NULL,
    new_quantity INTEGER NOT NULL CHECK (new_quantity >= 0),
    reason TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_stock_movements_prod ON stock_movements(product_id);
CREATE INDEX IF NOT EXISTS idx_stock_movements_time ON stock_movements(timestamp);

-- 3. Audit Logs Table (Q07 Feature 5)
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT NOT NULL DEFAULT 'PRODUCT',
    entity_id TEXT NOT NULL,
    action TEXT NOT NULL CHECK (action IN ('CREATE', 'UPDATE', 'DELETE', 'STOCK_ADJUSTMENT')),
    old_values TEXT, -- JSON representation
    new_values TEXT, -- JSON representation
    reason TEXT,
    timestamp TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_audit_entity ON audit_logs(entity_id);
CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs(timestamp);

-- 4. TQM Defect Log / Checksheet Table
CREATE TABLE IF NOT EXISTS defects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    defect_code TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL,
    description TEXT NOT NULL,
    severity TEXT NOT NULL CHECK (severity IN ('Low', 'Medium', 'High', 'Critical')),
    occurrence_count INTEGER NOT NULL DEFAULT 1 CHECK (occurrence_count >= 1),
    status TEXT NOT NULL DEFAULT 'Open' CHECK (status IN ('Open', 'Under Review', 'Resolved')),
    corrective_action TEXT,
    created_at TEXT NOT NULL,
    resolved_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_defects_category ON defects(category);
CREATE INDEX IF NOT EXISTS idx_defects_status ON defects(status);

-- 5. TQM FMEA Worksheet Table
CREATE TABLE IF NOT EXISTS fmea_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    process_step TEXT NOT NULL,
    failure_mode TEXT NOT NULL,
    failure_effect TEXT NOT NULL,
    potential_cause TEXT NOT NULL,
    existing_controls TEXT NOT NULL,
    severity INTEGER NOT NULL CHECK (severity BETWEEN 1 AND 10),
    occurrence INTEGER NOT NULL CHECK (occurrence BETWEEN 1 AND 10),
    detection INTEGER NOT NULL CHECK (detection BETWEEN 1 AND 10),
    rpn INTEGER NOT NULL,
    recommended_action TEXT NOT NULL,
    owner TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Open',
    created_at TEXT NOT NULL
);

-- 6. TQM PDCA Improvement Records Table
CREATE TABLE IF NOT EXISTS pdca_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    stage TEXT NOT NULL CHECK (stage IN ('PLAN', 'DO', 'CHECK', 'ACT')),
    problem_statement TEXT NOT NULL,
    plan_description TEXT NOT NULL,
    do_action TEXT,
    expected_result TEXT,
    actual_result TEXT,
    check_verification TEXT,
    act_standardization TEXT,
    owner TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Planned' CHECK (status IN ('Planned', 'In Progress', 'Completed', 'Needs Revision')),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- 7. Application Users Table (Authentication & RBAC)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE COLLATE NOCASE,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE COLLATE NOCASE,
    role TEXT NOT NULL DEFAULT 'Manager' CHECK (role IN ('Admin', 'Manager', 'Staff')),
    created_at TEXT NOT NULL,
    last_login TEXT
);

CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
"""


def current_iso_time() -> str:
    """Returns standard ISO formatted UTC timestamp."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def initialize_database(manager: DatabaseManager = db_manager) -> None:
    """Initializes all database tables and seed sample data if empty."""
    logger.info(f"Initializing database at path: {manager.db_path}")

    with manager.transaction() as conn:
        conn.executescript(SCHEMA_SQL)

        cursor = conn.cursor()

        # Check if users table has existing accounts
        cursor.execute("SELECT COUNT(*) AS count FROM users")
        user_count = cursor.fetchone()["count"]
        if user_count == 0:
            logger.info("Seeding initial administrator and staff user accounts...")
            seed_initial_users(conn)

        # Check if products table has existing records
        cursor.execute("SELECT COUNT(*) AS count FROM products")
        product_count = cursor.fetchone()["count"]

        if product_count == 0:
            logger.info("Empty database detected. Seeding initial baseline inventory...")
            seed_initial_products(conn)

        # Check if defects table has existing records
        cursor.execute("SELECT COUNT(*) AS count FROM defects")
        defect_count = cursor.fetchone()["count"]
        if defect_count == 0:
            logger.info("Seeding standard TQM checksheets and defect historical log...")
            seed_initial_defects(conn)

        # Check if FMEA has existing records
        cursor.execute("SELECT COUNT(*) AS count FROM fmea_items")
        fmea_count = cursor.fetchone()["count"]
        if fmea_count == 0:
            logger.info("Seeding TQM FMEA data accuracy analysis records...")
            seed_initial_fmea(conn)

        # Check if PDCA has existing records
        cursor.execute("SELECT COUNT(*) AS count FROM pdca_records")
        pdca_count = cursor.fetchone()["count"]
        if pdca_count == 0:
            logger.info("Seeding TQM PDCA cycles for Q07 Quality Goal...")
            seed_initial_pdca(conn)

    logger.info("Database schema verification and initialization completed successfully.")


def seed_initial_products(conn: sqlite3.Connection) -> None:
    """Seeds realistic initial inventory products and initial audit logs."""
    timestamp = current_iso_time()
    sample_products = [
        ("PRD-1001", "Precision Digital Caliper", "Electronics", "ELEC-CAL-01", 35, 1250.00, 10, "Apex Metrology Labs"),
        ("PRD-1002", "Anti-Static Cleanroom Gloves", "Accessories", "ACC-GLV-02", 150, 45.00, 40, "SafeTech Supplies"),
        ("PRD-1003", "Ergonomic Quality Inspection Chair", "Furniture", "FURN-CHR-03", 8, 4800.00, 5, "ErgoLine Works"),
        ("PRD-1004", "Optical Inspection Microscope", "Electronics", "ELEC-MIC-04", 4, 18500.00, 5, "VisionTech Instruments"),
        ("PRD-1005", "Industrial Quality Audit Logbook", "Stationery", "STAT-LOG-05", 85, 120.00, 20, "Apex Office Supplies"),
        ("PRD-1006", "High-Grade Stainless Steel Rods", "Raw Materials", "RAW-STE-06", 120, 320.00, 30, "Metallo Industrial Corp"),
        ("PRD-1007", "Digital Infrared Thermometer", "Electronics", "ELEC-THM-07", 22, 1650.00, 8, "Apex Metrology Labs"),
        ("PRD-1008", "Heavy-Duty Workstation Table", "Furniture", "FURN-TBL-08", 6, 8500.00, 3, "ErgoLine Works"),
        ("PRD-1009", "Barcoded Inventory Label Rolls", "Stationery", "STAT-LBL-09", 200, 95.00, 50, "SafeTech Supplies"),
        ("PRD-1010", "Alloy Calibration Weight Set", "Accessories", "ACC-WGT-10", 3, 3400.00, 5, "VisionTech Instruments"),
    ]

    for p in sample_products:
        conn.execute(
            """
            INSERT INTO products (product_id, name, category, sku, quantity, unit_price, reorder_level, supplier_name, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7], timestamp, timestamp),
        )

        # Record Initial Stock Movement
        conn.execute(
            """
            INSERT INTO stock_movements (product_id, movement_type, quantity_change, previous_quantity, new_quantity, reason, timestamp)
            VALUES (?, 'INITIAL', ?, 0, ?, 'Initial inventory stock load', ?)
            """,
            (p[0], p[4], p[4], timestamp),
        )

        # Record Initial Audit Log
        initial_dict = {
            "product_id": p[0],
            "name": p[1],
            "category": p[2],
            "sku": p[3],
            "quantity": p[4],
            "unit_price": p[5],
            "reorder_level": p[6],
            "supplier_name": p[7],
        }
        conn.execute(
            """
            INSERT INTO audit_logs (entity_type, entity_id, action, old_values, new_values, reason, timestamp)
            VALUES ('PRODUCT', ?, 'CREATE', NULL, ?, 'Initial baseline catalog seed', ?)
            """,
            (p[0], json.dumps(initial_dict), timestamp),
        )


def seed_initial_defects(conn: sqlite3.Connection) -> None:
    """Seeds historical defect checksheets for Pareto and CTQ analysis."""
    timestamp = current_iso_time()
    # Frequencies reflecting pre-TQM baseline data inaccuracy issues
    sample_defects = [
        ("DEF-1001", "Invalid Input", "Operator entered string in unit price field during purchase receipt", "High", 28, "Resolved", "Enforced strict regex and numeric parsing via Input Masking", timestamp, timestamp),
        ("DEF-1002", "Stock Mismatch", "Physical physical count did not reconcile with ledger quantity", "Critical", 19, "Resolved", "Introduced mandatory transactional stock adjustment log with reasons", timestamp, timestamp),
        ("DEF-1003", "Duplicate Identifier", "Duplicate SKU code manually created for different model", "High", 14, "Resolved", "Added SQLite UNIQUE constraint & pre-save SKU lookup", timestamp, timestamp),
        ("DEF-1004", "Incorrect Category", "Operator manually typed 'elect.' causing split reporting categories", "Medium", 11, "Resolved", "Replaced free-text entry with controlled dropdown list", timestamp, timestamp),
        ("DEF-1005", "Search Failure", "Search returned no records due to case sensitivity mismatch", "Low", 5, "Resolved", "Implemented case-insensitive LIKE parameterized query", timestamp, timestamp),
        ("DEF-1006", "Database Error", "Connection lock occurred during concurrent file write", "Medium", 3, "Resolved", "Enabled WAL mode and transaction context managers", timestamp, timestamp),
    ]

    for d in sample_defects:
        conn.execute(
            """
            INSERT INTO defects (defect_code, category, description, severity, occurrence_count, status, corrective_action, created_at, resolved_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            d,
        )


def seed_initial_fmea(conn: sqlite3.Connection) -> None:
    """Seeds FMEA analysis records for inventory data quality."""
    timestamp = current_iso_time()
    sample_fmea = [
        (
            "Product Registration",
            "Malformed SKU Entered",
            "Barcode scan fails at dispatch; item cannot be tracked",
            "Manual typo by clerk during rapid receipt entry",
            "Visual check by operator",
            7, 6, 6, 252, # RPN = 7 * 6 * 6 = 252
            "Implement automated SKU regex mask and verification button",
            "Quality Lead",
            "Implemented",
            timestamp,
        ),
        (
            "Stock Receipt",
            "Negative Quantity Entry",
            "Corrupts inventory valuation and causes false reorder signals",
            "Clerk enters signed number (-10) instead of outward transaction",
            "None in legacy system",
            8, 5, 5, 200, # RPN = 8 * 5 * 5 = 200
            "Enforce SQLite CHECK (quantity >= 0) and service validator",
            "Software SDE",
            "Implemented",
            timestamp,
        ),
        (
            "Category Assignment",
            "Category Inconsistency",
            "Distorted category Pareto and inventory financial reports",
            "Free-form text input with inconsistent spelling variations",
            "Manual Excel review",
            5, 7, 5, 175, # RPN = 5 * 7 * 5 = 175
            "Enforce controlled dropdown list with fixed master categories",
            "UI Designer",
            "Implemented",
            timestamp,
        ),
        (
            "Product Deletion",
            "Accidental Catalog Deletion",
            "Permanent data loss; orphaned historical inventory items",
            "Accidental click on Delete button without safeguard",
            "None in legacy system",
            9, 3, 6, 162, # RPN = 9 * 3 * 6 = 162
            "Introduce confirmation modal with explicit item details and audit trail",
            "Quality Lead",
            "Implemented",
            timestamp,
        ),
        (
            "Stock Adjustment",
            "Unaccounted Stock Variance",
            "Physical and software inventory desynchronization",
            "Adjustments made without documenting reason or authorizer",
            "Periodic annual audit",
            8, 4, 4, 128, # RPN = 8 * 4 * 4 = 128
            "Mandate stock movement transaction log with reason requirement",
            "Operations Manager",
            "Implemented",
            timestamp,
        ),
    ]

    for item in sample_fmea:
        conn.execute(
            """
            INSERT INTO fmea_items (process_step, failure_mode, failure_effect, potential_cause, existing_controls,
                                    severity, occurrence, detection, rpn, recommended_action, owner, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            item,
        )


def seed_initial_pdca(conn: sqlite3.Connection) -> None:
    """Seeds PDCA improvement cycle entries demonstrating TQM execution."""
    timestamp = current_iso_time()
    sample_pdca = [
        (
            "Phase 1: Input Quality Control & Masking",
            "ACT",
            "High rate of invalid numeric entries and negative stock in legacy inventory system.",
            "Design input validation rules, masking, and regex checks for all user entry forms.",
            "Implemented ProductValidator class and bound live validation handlers to CTk entries.",
            "Zero invalid numeric entries submitted to database during operational cycle.",
            "Achieved 100% rejection rate for malformed data inputs in automated testing.",
            "Unit test suite validating 15 boundary cases; zero validation bypasses in audit log.",
            "Standardize ProductValidator as mandatory gatekeeper for all data entry endpoints.",
            "Operations Lead",
            "Completed",
            timestamp,
            timestamp,
        ),
        (
            "Phase 2: Category Standardization & Referential Integrity",
            "ACT",
            "Fragmented category naming (e.g. 'Elec', 'Electronics', 'ELECT') distorting inventory analytics.",
            "Enforce controlled category dropdown selector restricting entries to 6 standardized groups.",
            "Integrated CustomTkinter OptionMenu populated from authoritative configuration constants.",
            "Eliminate all category spelling variants and ensure clean Pareto distribution analysis.",
            "Audit records show 100% compliance with master category catalog.",
            "Database integrity scan querying distinct categories; verified exact match to allowed list.",
            "Document master category catalog in System Architecture documentation.",
            "Operations Lead",
            "Completed",
            timestamp,
            timestamp,
        ),
        (
            "Phase 3: Transactional Audit Trail & Change Logging",
            "DO",
            "Lack of traceability for unauthorized stock adjustments and missing accountability.",
            "Architect dedicated audit_logs table capturing JSON diffs of previous and updated values.",
            "Created AuditService and integrated transactional hooks on all Create, Update, Delete events.",
            "Every database change is paired with an immutable audit record containing old and new values.",
            "In progress: verifying audit log viewer performance with large log volumes.",
            "Verify matching audit record exists for every product table row modification.",
            "Deploy audit log export and search filtering in management dashboard.",
            "Operations Lead",
            "In Progress",
            timestamp,
            timestamp,
        ),
    ]

    for r in sample_pdca:
        conn.execute(
            """
            INSERT INTO pdca_records (title, stage, problem_statement, plan_description, do_action,
                                      expected_result, actual_result, check_verification, act_standardization,
                                      owner, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            r,
        )


def seed_initial_users(conn: sqlite3.Connection) -> None:
    """Seeds default system user accounts for authentication and role-based access."""
    import hashlib
    import secrets

    def hash_pwd(pwd: str) -> tuple[str, str]:
        salt = secrets.token_hex(16)
        key = hashlib.pbkdf2_hmac("sha256", pwd.encode("utf-8"), salt.encode("utf-8"), 100000)
        return key.hex(), salt

    timestamp = current_iso_time()

    admin_hash, admin_salt = hash_pwd("admin123")
    manager_hash, manager_salt = hash_pwd("manager123")
    staff_hash, staff_salt = hash_pwd("staff123")

    sample_users = [
        ("admin", admin_hash, admin_salt, "System Administrator", "admin@inventory.local", "Admin", timestamp),
        ("manager", manager_hash, manager_salt, "Inventory Manager", "manager@inventory.local", "Manager", timestamp),
        ("staff", staff_hash, staff_salt, "Warehouse Staff", "staff@inventory.local", "Staff", timestamp),
    ]

    for u in sample_users:
        conn.execute(
            """
            INSERT INTO users (username, password_hash, salt, full_name, email, role, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            u,
        )

