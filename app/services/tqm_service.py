"""TQM Service: CTQ indicators, Defect Checksheets, Pareto Analysis, FMEA, Fishbone, SIPOC, and PDCA."""

from typing import Any, Dict, List, Optional, Tuple
from app.config import ALLOWED_CATEGORIES
from app.database.connection import DatabaseManager, db_manager
from app.database.schema import current_iso_time
from app.models.tqm import Defect, FMEAItem, PDCARecord
from app.utils.logger import logger
from app.utils.validators import ProductValidator, ValidationError


class TQMService:
    """Implements statistical quality control and continuous improvement algorithms for BBAT104."""

    def __init__(self, manager: DatabaseManager = db_manager):
        self.manager = manager

    # =========================================================================
    # A. CTQ (Critical to Quality) METRICS
    # =========================================================================
    def calculate_ctq_metrics(self) -> Dict[str, Any]:
        """Calculates dynamic Critical to Quality (CTQ) indicators from live SQLite records."""
        with self.manager.get_connection() as conn:
            cursor = conn.cursor()

            # 1. Product Quantity Accuracy (Negative / Non-Integer check)
            cursor.execute("SELECT COUNT(*) AS total, SUM(CASE WHEN quantity < 0 THEN 1 ELSE 0 END) AS invalid_qty FROM products")
            row_qty = cursor.fetchone()
            total_prods = row_qty["total"] or 0
            invalid_qty = row_qty["invalid_qty"] or 0
            qty_accuracy_pct = 100.0 if total_prods == 0 else round(((total_prods - invalid_qty) / total_prods) * 100, 2)

            # 2. SKU Uniqueness & Format Compliance
            cursor.execute("SELECT COUNT(DISTINCT sku) AS unique_skus, COUNT(sku) AS total_skus FROM products")
            row_sku = cursor.fetchone()
            unique_skus = row_sku["unique_skus"] or 0
            total_skus = row_sku["total_skus"] or 0
            sku_uniqueness_pct = 100.0 if total_skus == 0 else round((unique_skus / total_skus) * 100, 2)

            # 3. Mandatory Fields Completeness
            cursor.execute(
                """
                SELECT COUNT(*) AS incomplete
                FROM products
                WHERE TRIM(name) = '' OR TRIM(category) = '' OR TRIM(sku) = '' OR TRIM(supplier_name) = '' OR unit_price <= 0
                """
            )
            incomplete_count = cursor.fetchone()["incomplete"] or 0
            completeness_pct = 100.0 if total_prods == 0 else round(((total_prods - incomplete_count) / total_prods) * 100, 2)

            # 4. Category Standardization Compliance
            placeholders = ",".join("?" for _ in ALLOWED_CATEGORIES)
            cursor.execute(
                f"SELECT COUNT(*) AS non_standard FROM products WHERE category NOT IN ({placeholders})",
                ALLOWED_CATEGORIES,
            )
            non_std_categories = cursor.fetchone()["non_standard"] or 0
            category_compliance_pct = 100.0 if total_prods == 0 else round(((total_prods - non_std_categories) / total_prods) * 100, 2)

            # 5. Audit Traceability Coverage
            cursor.execute("SELECT COUNT(*) AS audit_count FROM audit_logs")
            audit_count = cursor.fetchone()["audit_count"] or 0

            cursor.execute("SELECT COUNT(*) AS movement_count FROM stock_movements")
            movement_count = cursor.fetchone()["movement_count"] or 0

            # CTQ Scorecard
            return {
                "total_products": total_prods,
                "metrics": [
                    {
                        "ctq_id": "CTQ-1",
                        "characteristic": "Stock Quantity Integrity",
                        "operational_definition": "Percentage of products with verified non-negative integer stock",
                        "target": "100.0%",
                        "actual": f"{qty_accuracy_pct:.1f}%",
                        "status": "PASS" if qty_accuracy_pct == 100.0 else "FAIL",
                        "defect_count": invalid_qty,
                    },
                    {
                        "ctq_id": "CTQ-2",
                        "characteristic": "Identifier Uniqueness (SKU)",
                        "operational_definition": "Ratio of distinct SKUs to total product catalog entries",
                        "target": "100.0%",
                        "actual": f"{sku_uniqueness_pct:.1f}%",
                        "status": "PASS" if sku_uniqueness_pct == 100.0 else "FAIL",
                        "defect_count": total_skus - unique_skus,
                    },
                    {
                        "ctq_id": "CTQ-3",
                        "characteristic": "Data Completeness",
                        "operational_definition": "Zero blank mandatory fields (Name, SKU, Category, Price, Supplier)",
                        "target": "100.0%",
                        "actual": f"{completeness_pct:.1f}%",
                        "status": "PASS" if completeness_pct == 100.0 else "FAIL",
                        "defect_count": incomplete_count,
                    },
                    {
                        "ctq_id": "CTQ-4",
                        "characteristic": "Category Standardization",
                        "operational_definition": "Adherence to controlled 6-category master classification",
                        "target": "100.0%",
                        "actual": f"{category_compliance_pct:.1f}%",
                        "status": "PASS" if category_compliance_pct == 100.0 else "FAIL",
                        "defect_count": non_std_categories,
                    },
                    {
                        "ctq_id": "CTQ-5",
                        "characteristic": "Audit Trail Traceability",
                        "operational_definition": "Transactional audit coverage for all catalog operations",
                        "target": ">= 100%",
                        "actual": f"{audit_count} entries recorded",
                        "status": "PASS" if audit_count >= total_prods else "WARNING",
                        "defect_count": 0,
                    },
                ],
                "summary": {
                    "audit_entries": audit_count,
                    "stock_movements": movement_count,
                },
            }

    # =========================================================================
    # B. DEFECT LOG / CHECKSHEET
    # =========================================================================
    def get_all_defects(self, status_filter: str = "All") -> List[Defect]:
        """Fetches all defect checksheets."""
        query = "SELECT * FROM defects"
        params: List[Any] = []
        if status_filter and status_filter != "All":
            query += " WHERE status = ?"
            params.append(status_filter)
        query += " ORDER BY id DESC"

        with self.manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [Defect.from_row(r) for r in cursor.fetchall()]

    def add_defect(
        self,
        category: str,
        description: str,
        severity: str,
        occurrence_count: int = 1,
        corrective_action: str = "",
    ) -> Defect:
        """Adds a newly observed defect entry into the TQM checksheet."""
        cleaned_cat = ProductValidator.normalize_text(category)
        cleaned_desc = ProductValidator.normalize_text(description)
        if not cleaned_desc:
            raise ValidationError("Defect description is mandatory.", field="description")
        if occurrence_count < 1:
            raise ValidationError("Occurrence count must be at least 1.", field="occurrence_count")

        now = current_iso_time()

        with self.manager.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) AS count FROM defects")
            cnt = cursor.fetchone()["count"]
            code = f"DEF-{cnt + 1001}"

            cursor.execute(
                """
                INSERT INTO defects (defect_code, category, description, severity, occurrence_count, status, corrective_action, created_at)
                VALUES (?, ?, ?, ?, ?, 'Open', ?, ?)
                """,
                (code, cleaned_cat, cleaned_desc, severity, occurrence_count, corrective_action, now),
            )
            d_id = cursor.lastrowid

        logger.info(f"Defect '{code}' ({cleaned_cat}) logged.")
        return Defect(
            id=d_id,
            defect_code=code,
            category=cleaned_cat,
            description=cleaned_desc,
            severity=severity,
            occurrence_count=occurrence_count,
            status="Open",
            corrective_action=corrective_action,
            created_at=now,
        )

    def resolve_defect(self, defect_code: str, corrective_action: str) -> bool:
        """Marks a defect as Resolved with documented corrective action."""
        now = current_iso_time()
        with self.manager.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE defects
                SET status = 'Resolved', corrective_action = ?, resolved_at = ?
                WHERE defect_code = ?
                """,
                (corrective_action, now, defect_code),
            )
            return cursor.rowcount > 0

    # =========================================================================
    # C. PARETO ANALYSIS (80/20 Rule)
    # =========================================================================
    def calculate_pareto_data(self) -> Dict[str, Any]:
        """Calculates Pareto distribution: categories, counts, cumulative counts, cumulative percentages."""
        with self.manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT category, SUM(occurrence_count) AS total_count
                FROM defects
                GROUP BY category
                ORDER BY total_count DESC
                """
            )
            rows = cursor.fetchall()

        if not rows:
            return {
                "categories": [],
                "counts": [],
                "cumulative_counts": [],
                "cumulative_percentages": [],
                "total_defects": 0,
                "vital_few": [],
            }

        categories = [r["category"] for r in rows]
        counts = [r["total_count"] for r in rows]
        total_defects = sum(counts)

        cumulative_counts = []
        cumulative_percentages = []
        running_sum = 0
        vital_few = []

        for cat, cnt in zip(categories, counts):
            running_sum += cnt
            cumulative_counts.append(running_sum)
            pct = round((running_sum / total_defects) * 100, 2) if total_defects > 0 else 0.0
            cumulative_percentages.append(pct)
            if pct <= 80.0 or (len(vital_few) == 0 and pct > 80.0):
                vital_few.append(cat)

        return {
            "categories": categories,
            "counts": counts,
            "cumulative_counts": cumulative_counts,
            "cumulative_percentages": cumulative_percentages,
            "total_defects": total_defects,
            "vital_few": vital_few,
        }

    # =========================================================================
    # D. FISHBONE / ISHIKAWA CAUSE-AND-EFFECT ANALYSIS
    # =========================================================================
    def get_fishbone_data(self) -> Dict[str, Any]:
        """Returns structured 4M/course cause categories for inventory data inaccuracies."""
        return {
            "problem_statement": "Inventory Data Inaccuracy (Quality Goal Q07)",
            "categories": {
                "People": [
                    "Lack of standardized onboarding on SKU format rules",
                    "Fatigue during rapid end-of-day purchase receipt entry",
                    "Typographical errors in decimal unit price input",
                    "Assumed categories due to missing written standard",
                ],
                "Process": [
                    "Unconfirmed stock adjustments without supervisor sign-off",
                    "Delayed physical inventory reconciliation cycles",
                    "No immediate error feedback when invalid data is keyed in",
                    "Uncontrolled category variations (e.g. abbreviations)",
                ],
                "Software Code": [
                    "Absence of input regex validation and masking in UI",
                    "Unchecked negative quantity submissions into database",
                    "Case-sensitive search failing to find existing items",
                    "Lack of atomic transaction rollback on multi-table updates",
                ],
                "Infrastructure": [
                    "Barcode scanner misreads due to smudged label print",
                    "Unreliable local SQLite file locks during simultaneous access",
                    "Lack of automated database backups before bulk operations",
                    "Poor screen contrast on terminal causing visual fatigue",
                ],
            },
        }

    # =========================================================================
    # E. FMEA (Failure Mode and Effects Analysis)
    # =========================================================================
    def get_all_fmea(self) -> List[FMEAItem]:
        """Fetches all FMEA records sorted by RPN descending."""
        with self.manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM fmea_items ORDER BY rpn DESC")
            return [FMEAItem.from_row(r) for r in cursor.fetchall()]

    def add_fmea_item(
        self,
        process_step: str,
        failure_mode: str,
        failure_effect: str,
        potential_cause: str,
        existing_controls: str,
        severity: int,
        occurrence: int,
        detection: int,
        recommended_action: str,
        owner: str,
    ) -> FMEAItem:
        """Validates 1-10 scores, computes RPN, and stores FMEA record."""
        for score_name, val in [("Severity", severity), ("Occurrence", occurrence), ("Detection", detection)]:
            if not isinstance(val, int) or val < 1 or val > 10:
                raise ValidationError(f"{score_name} score must be an integer between 1 and 10.", field=score_name.lower())

        rpn = severity * occurrence * detection
        now = current_iso_time()

        with self.manager.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO fmea_items (process_step, failure_mode, failure_effect, potential_cause, existing_controls,
                                        severity, occurrence, detection, rpn, recommended_action, owner, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Open', ?)
                """,
                (
                    process_step,
                    failure_mode,
                    failure_effect,
                    potential_cause,
                    existing_controls,
                    severity,
                    occurrence,
                    detection,
                    rpn,
                    recommended_action,
                    owner,
                    now,
                ),
            )
            item_id = cursor.lastrowid

        logger.info(f"FMEA Item added: '{failure_mode}', RPN={rpn}")
        return FMEAItem(
            id=item_id,
            process_step=process_step,
            failure_mode=failure_mode,
            failure_effect=failure_effect,
            potential_cause=potential_cause,
            existing_controls=existing_controls,
            severity=severity,
            occurrence=occurrence,
            detection=detection,
            rpn=rpn,
            recommended_action=recommended_action,
            owner=owner,
            status="Open",
            created_at=now,
        )

    # =========================================================================
    # F. SIPOC PROCESS MAP
    # =========================================================================
    def get_sipoc_data(self) -> Dict[str, Any]:
        """Returns structured SIPOC workflow matrix for the inventory management lifecycle."""
        return {
            "title": "Inventory Lifecycle Quality Process Map (SIPOC)",
            "columns": ["Suppliers", "Inputs", "Process Steps", "Outputs", "Customers"],
            "stages": [
                {
                    "suppliers": "Vendors & Equipment Distributors",
                    "inputs": "Purchase Orders, Delivery Invoices, Physical Goods",
                    "process": "1. Receipt & Goods Inward Verification",
                    "outputs": "Verified Goods Delivery Note (GDN), Physical Stock",
                    "customers": "Warehouse Receiving Clerks",
                },
                {
                    "suppliers": "Receiving Clerks",
                    "inputs": "GDN, Item Specifications, Barcode Labels",
                    "process": "2. Product Catalog Registration (Q07 Input Masking)",
                    "outputs": "Validated Product Record, Assigned SKU, System ID",
                    "customers": "Inventory Management System",
                },
                {
                    "suppliers": "System Operators",
                    "inputs": "Categorized Product Data, Reorder Thresholds",
                    "process": "3. Storage & Stock Allocation (Controlled Categories)",
                    "outputs": "Accurate Stock Ledger, Storage Bin Assignment",
                    "customers": "Store Supervisors",
                },
                {
                    "suppliers": "Internal Departments / Buyers",
                    "inputs": "Requisition Orders, Issue Slips, Stock Counts",
                    "process": "4. Stock Issue & Adjustment (Audit Logging & Confirmation)",
                    "outputs": "Stock Movement Transaction, Dispatched Goods, JSON Audit Log",
                    "customers": "End Users & Production Lines",
                },
                {
                    "suppliers": "Inventory System Database",
                    "inputs": "Stock Ledger, Valuation Records, Defect Logs",
                    "process": "5. Quality Audit & Analytics (Pareto & FMEA Evaluation)",
                    "outputs": "CTQ Scorecard, Pareto 80/20 Chart, PDCA Action Plan",
                    "customers": "TQM Committee, Plant Management, Finance",
                },
            ],
        }

    # =========================================================================
    # G. PDCA IMPROVEMENT TRACKER
    # =========================================================================
    def get_all_pdca(self) -> List[PDCARecord]:
        """Fetches all PDCA cycle records."""
        with self.manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM pdca_records ORDER BY id ASC")
            return [PDCARecord.from_row(r) for r in cursor.fetchall()]

    def add_pdca_record(
        self,
        title: str,
        stage: str,
        problem_statement: str,
        plan_description: str,
        owner: str,
        status: str = "Planned",
        do_action: str = "",
        expected_result: str = "",
        actual_result: str = "",
        check_verification: str = "",
        act_standardization: str = "",
    ) -> PDCARecord:
        """Creates a new PDCA continuous improvement cycle record."""
        now = current_iso_time()
        with self.manager.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO pdca_records (title, stage, problem_statement, plan_description, do_action,
                                          expected_result, actual_result, check_verification, act_standardization,
                                          owner, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    title,
                    stage,
                    problem_statement,
                    plan_description,
                    do_action,
                    expected_result,
                    actual_result,
                    check_verification,
                    act_standardization,
                    owner,
                    status,
                    now,
                    now,
                ),
            )
            rec_id = cursor.lastrowid

        logger.info(f"PDCA Record created: '{title}' [{stage}]")
        return PDCARecord(
            id=rec_id,
            title=title,
            stage=stage,
            problem_statement=problem_statement,
            plan_description=plan_description,
            do_action=do_action,
            expected_result=expected_result,
            actual_result=actual_result,
            check_verification=check_verification,
            act_standardization=act_standardization,
            owner=owner,
            status=status,
            created_at=now,
            updated_at=now,
        )

    def update_pdca_stage(
        self,
        record_id: int,
        stage: str,
        status: str,
        do_action: Optional[str] = None,
        actual_result: Optional[str] = None,
        check_verification: Optional[str] = None,
        act_standardization: Optional[str] = None,
    ) -> bool:
        """Updates the active stage and execution notes of a PDCA record."""
        now = current_iso_time()
        with self.manager.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE pdca_records
                SET stage = ?, status = ?,
                    do_action = COALESCE(?, do_action),
                    actual_result = COALESCE(?, actual_result),
                    check_verification = COALESCE(?, check_verification),
                    act_standardization = COALESCE(?, act_standardization),
                    updated_at = ?
                WHERE id = ?
                """,
                (stage, status, do_action, actual_result, check_verification, act_standardization, now, record_id),
            )
            return cursor.rowcount > 0
