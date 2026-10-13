"""Product Service managing CRUD operations, transactional audit logging, and search."""

import json
import sqlite3
from typing import Any, Dict, List, Optional, Tuple
from app.database.connection import DatabaseManager, db_manager
from app.database.schema import current_iso_time
from app.models.product import Product
from app.utils.logger import logger
from app.utils.validators import ProductValidator, ValidationError, compute_dict_diff


class ProductService:
    """Provides product catalog management with strict data validation and audit logging."""

    def __init__(self, manager: DatabaseManager = db_manager):
        self.manager = manager

    def generate_next_product_id(self) -> str:
        """Generates the next sequential product identifier (e.g., PRD-1011)."""
        with self.manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT product_id FROM products ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            if not row:
                return "PRD-1001"
            last_id = row["product_id"]
            try:
                numeric_part = int(last_id.split("-")[1])
                return f"PRD-{numeric_part + 1:04d}"
            except Exception:
                cursor.execute("SELECT COUNT(*) AS total FROM products")
                count = cursor.fetchone()["total"]
                return f"PRD-{count + 1001:04d}"

    def check_sku_exists(self, sku: str, exclude_product_id: Optional[str] = None) -> bool:
        """Checks if a SKU is already registered to another active product."""
        normalized_sku = sku.strip().upper()
        with self.manager.get_connection() as conn:
            cursor = conn.cursor()
            if exclude_product_id:
                cursor.execute(
                    "SELECT 1 FROM products WHERE UPPER(sku) = ? AND product_id != ?",
                    (normalized_sku, exclude_product_id),
                )
            else:
                cursor.execute("SELECT 1 FROM products WHERE UPPER(sku) = ?", (normalized_sku,))
            return cursor.fetchone() is not None

    def create_product(self, data: Dict[str, Any], change_reason: str = "New product registration") -> Product:
        """Validates and creates a new product with atomic audit logging and stock movement entry."""
        validated = ProductValidator.validate_product_data(data)
        sku = validated["sku"]

        if self.check_sku_exists(sku):
            raise ValidationError(f"SKU code '{sku}' is already in use by another product.", field="sku")

        product_id = self.generate_next_product_id()
        now = current_iso_time()

        with self.manager.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO products (product_id, name, category, sku, quantity, unit_price, reorder_level, supplier_name, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    product_id,
                    validated["name"],
                    validated["category"],
                    sku,
                    validated["quantity"],
                    validated["unit_price"],
                    validated["reorder_level"],
                    validated["supplier_name"],
                    now,
                    now,
                ),
            )

            # Record initial stock movement if quantity > 0
            if validated["quantity"] > 0:
                cursor.execute(
                    """
                    INSERT INTO stock_movements (product_id, movement_type, quantity_change, previous_quantity, new_quantity, reason, timestamp)
                    VALUES (?, 'INITIAL', ?, 0, ?, ?, ?)
                    """,
                    (product_id, validated["quantity"], validated["quantity"], change_reason, now),
                )

            # Record audit log
            audit_dict = {
                "product_id": product_id,
                **validated,
            }
            cursor.execute(
                """
                INSERT INTO audit_logs (entity_type, entity_id, action, old_values, new_values, reason, timestamp)
                VALUES ('PRODUCT', ?, 'CREATE', NULL, ?, ?, ?)
                """,
                (product_id, json.dumps(audit_dict), change_reason, now),
            )

        logger.info(f"Product '{product_id}' ({validated['name']}) created successfully.")
        return self.get_product_by_id(product_id)

    def get_product_by_id(self, product_id: str) -> Optional[Product]:
        """Fetches a single product by its unique product_id."""
        with self.manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products WHERE product_id = ?", (product_id,))
            row = cursor.fetchone()
            return Product.from_row(row) if row else None

    def get_all_products(
        self,
        search_query: str = "",
        category_filter: str = "All",
        sort_by: str = "product_id",
        sort_ascending: bool = True,
    ) -> List[Product]:
        """Queries products with search, category filtering, and sorting."""
        valid_sort_columns = {
            "product_id": "product_id",
            "name": "name",
            "category": "category",
            "sku": "sku",
            "quantity": "quantity",
            "unit_price": "unit_price",
            "reorder_level": "reorder_level",
            "supplier_name": "supplier_name",
        }
        order_col = valid_sort_columns.get(sort_by, "product_id")
        order_dir = "ASC" if sort_ascending else "DESC"

        query = "SELECT * FROM products WHERE 1=1"
        params: List[Any] = []

        if category_filter and category_filter != "All":
            query += " AND category = ?"
            params.append(category_filter)

        if search_query:
            cleaned_search = f"%{search_query.strip().lower()}%"
            query += " AND (LOWER(name) LIKE ? OR LOWER(sku) LIKE ? OR LOWER(product_id) LIKE ? OR LOWER(supplier_name) LIKE ?)"
            params.extend([cleaned_search, cleaned_search, cleaned_search, cleaned_search])

        query += f" ORDER BY {order_col} {order_dir}"

        with self.manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [Product.from_row(r) for r in rows]

    def search_autocomplete(self, query: str, limit: int = 8) -> List[Dict[str, str]]:
        """Q07 Feature 3: Auto-complete suggestion service querying actual product records."""
        cleaned = query.strip().lower()
        if not cleaned:
            return []

        search_pat = f"%{cleaned}%"
        with self.manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT product_id, name, sku, category, quantity, unit_price
                FROM products
                WHERE LOWER(name) LIKE ? OR LOWER(sku) LIKE ? OR LOWER(product_id) LIKE ?
                ORDER BY name ASC
                LIMIT ?
                """,
                (search_pat, search_pat, search_pat, limit),
            )
            rows = cursor.fetchall()
            results = []
            for r in rows:
                results.append({
                    "product_id": r["product_id"],
                    "name": r["name"],
                    "sku": r["sku"],
                    "category": r["category"],
                    "quantity": str(r["quantity"]),
                    "unit_price": f"${r['unit_price']:.2f}",
                    "display": f"{r['name']} ({r['sku']}) - {r['product_id']}",
                })
            return results

    def update_product(
        self, product_id: str, new_data: Dict[str, Any], change_reason: str = "Standard update"
    ) -> Product:
        """Transactionally updates product details, validates fields, and records JSON diff audit trail."""
        existing = self.get_product_by_id(product_id)
        if not existing:
            raise ValidationError(f"Product '{product_id}' not found.", field="product_id")

        validated = ProductValidator.validate_product_data(new_data)
        new_sku = validated["sku"]

        if self.check_sku_exists(new_sku, exclude_product_id=product_id):
            raise ValidationError(f"SKU code '{new_sku}' is already assigned to another product.", field="sku")

        old_dict = existing.to_dict()
        diff = compute_dict_diff(old_dict, validated)

        # If nothing changed, return existing
        if not diff:
            return existing

        now = current_iso_time()

        with self.manager.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE products
                SET name = ?, category = ?, sku = ?, quantity = ?, unit_price = ?,
                    reorder_level = ?, supplier_name = ?, updated_at = ?
                WHERE product_id = ?
                """,
                (
                    validated["name"],
                    validated["category"],
                    new_sku,
                    validated["quantity"],
                    validated["unit_price"],
                    validated["reorder_level"],
                    validated["supplier_name"],
                    now,
                    product_id,
                ),
            )

            # If quantity changed in product update, record stock movement
            if existing.quantity != validated["quantity"]:
                qty_diff = validated["quantity"] - existing.quantity
                m_type = "IN" if qty_diff > 0 else "OUT"
                cursor.execute(
                    """
                    INSERT INTO stock_movements (product_id, movement_type, quantity_change, previous_quantity, new_quantity, reason, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (product_id, m_type, qty_diff, existing.quantity, validated["quantity"], f"Product Update: {change_reason}", now),
                )

            # Record audit log with JSON representations of changes
            cursor.execute(
                """
                INSERT INTO audit_logs (entity_type, entity_id, action, old_values, new_values, reason, timestamp)
                VALUES ('PRODUCT', ?, 'UPDATE', ?, ?, ?, ?)
                """,
                (
                    product_id,
                    json.dumps(old_dict),
                    json.dumps(validated),
                    change_reason,
                    now,
                ),
            )

        logger.info(f"Product '{product_id}' updated successfully. Diffs: {list(diff.keys())}")
        return self.get_product_by_id(product_id)

    def delete_product(self, product_id: str, reason: str = "Catalog retirement") -> bool:
        """Deletes a product transactionally and records a full DELETE audit log."""
        existing = self.get_product_by_id(product_id)
        if not existing:
            raise ValidationError(f"Cannot delete non-existent product '{product_id}'.", field="product_id")

        old_dict = existing.to_dict()
        now = current_iso_time()

        with self.manager.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM products WHERE product_id = ?", (product_id,))
            cursor.execute(
                """
                INSERT INTO audit_logs (entity_type, entity_id, action, old_values, new_values, reason, timestamp)
                VALUES ('PRODUCT', ?, 'DELETE', ?, NULL, ?, ?)
                """,
                (product_id, json.dumps(old_dict), reason, now),
            )

        logger.info(f"Product '{product_id}' deleted successfully. Audit trail preserved.")
        return True
