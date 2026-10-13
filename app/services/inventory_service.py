"""Inventory Management Service handling stock adjustments, valuations, and movement history."""

import json
from typing import Any, Dict, List, Optional
from app.database.connection import DatabaseManager, db_manager
from app.database.schema import current_iso_time
from app.models.stock_movement import StockMovement
from app.models.product import Product
from app.utils.logger import logger
from app.utils.validators import ProductValidator, ValidationError


class InventoryService:
    """Manages stock quantity adjustments, movement tracking, and valuation calculations."""

    def __init__(self, manager: DatabaseManager = db_manager):
        self.manager = manager

    def adjust_stock(
        self,
        product_id: str,
        new_quantity: int,
        reason: str,
    ) -> StockMovement:
        """Applies a strict, transactional stock adjustment and records movement + audit logs."""
        cleaned_reason = ProductValidator.normalize_text(reason)
        if not cleaned_reason:
            raise ValidationError("An explicit adjustment reason is required for stock auditing.", field="reason")

        parsed_qty = ProductValidator.validate_quantity(new_quantity)

        now = current_iso_time()

        with self.manager.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products WHERE product_id = ?", (product_id,))
            row = cursor.fetchone()
            if not row:
                raise ValidationError(f"Product '{product_id}' not found.", field="product_id")

            existing_prod = Product.from_row(row)
            prev_qty = existing_prod.quantity
            qty_change = parsed_qty - prev_qty

            if qty_change == 0:
                raise ValidationError(
                    f"New quantity ({parsed_qty}) is identical to current stock. No adjustment needed.",
                    field="new_quantity",
                )

            # Update product quantity
            cursor.execute(
                "UPDATE products SET quantity = ?, updated_at = ? WHERE product_id = ?",
                (parsed_qty, now, product_id),
            )

            movement_type = "IN" if qty_change > 0 else "OUT"

            # Record stock movement
            cursor.execute(
                """
                INSERT INTO stock_movements (product_id, movement_type, quantity_change, previous_quantity, new_quantity, reason, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (product_id, movement_type, qty_change, prev_qty, parsed_qty, cleaned_reason, now),
            )
            movement_id = cursor.lastrowid

            # Record audit log
            old_data = {"quantity": prev_qty}
            new_data = {"quantity": parsed_qty, "change": qty_change}
            cursor.execute(
                """
                INSERT INTO audit_logs (entity_type, entity_id, action, old_values, new_values, reason, timestamp)
                VALUES ('PRODUCT', ?, 'STOCK_ADJUSTMENT', ?, ?, ?, ?)
                """,
                (product_id, json.dumps(old_data), json.dumps(new_data), cleaned_reason, now),
            )

        logger.info(
            f"Stock adjusted for '{product_id}': {prev_qty} -> {parsed_qty} ({movement_type} {abs(qty_change)}). Reason: {cleaned_reason}"
        )

        return StockMovement(
            id=movement_id,
            product_id=product_id,
            movement_type=movement_type,
            quantity_change=qty_change,
            previous_quantity=prev_qty,
            new_quantity=parsed_qty,
            reason=cleaned_reason,
            timestamp=now,
        )

    def get_stock_movements(
        self, product_id: Optional[str] = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Retrieves stock movement history joined with product metadata."""
        query = """
            SELECT sm.*, p.name AS product_name, p.sku AS product_sku
            FROM stock_movements sm
            LEFT JOIN products p ON sm.product_id = p.product_id
        """
        params: List[Any] = []
        if product_id:
            query += " WHERE sm.product_id = ?"
            params.append(product_id)

        query += " ORDER BY sm.id DESC LIMIT ?"
        params.append(limit)

        with self.manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def get_inventory_summary(self) -> Dict[str, Any]:
        """Calculates aggregate dashboard metrics directly from SQLite."""
        with self.manager.get_connection() as conn:
            cursor = conn.cursor()

            # Unique products and total units
            cursor.execute(
                """
                SELECT
                    COUNT(*) AS total_products,
                    COALESCE(SUM(quantity), 0) AS total_units,
                    COALESCE(SUM(quantity * unit_price), 0.0) AS total_valuation,
                    COALESCE(SUM(CASE WHEN quantity <= reorder_level THEN 1 ELSE 0 END), 0) AS low_stock_count
                FROM products
                """
            )
            agg = cursor.fetchone()

            # Category distribution
            cursor.execute(
                """
                SELECT
                    category,
                    COUNT(*) AS product_count,
                    COALESCE(SUM(quantity), 0) AS units,
                    COALESCE(SUM(quantity * unit_price), 0.0) AS valuation
                FROM products
                GROUP BY category
                ORDER BY valuation DESC
                """
            )
            cat_rows = cursor.fetchall()

            # Recent 5 activity logs
            cursor.execute(
                """
                SELECT al.*, p.name AS product_name
                FROM audit_logs al
                LEFT JOIN products p ON al.entity_id = p.product_id
                ORDER BY al.id DESC
                LIMIT 6
                """
            )
            recent_activities = [dict(r) for r in cursor.fetchall()]

            return {
                "total_products": agg["total_products"],
                "total_units": agg["total_units"],
                "total_valuation": round(agg["total_valuation"], 2),
                "low_stock_count": agg["low_stock_count"],
                "category_breakdown": [dict(r) for r in cat_rows],
                "recent_activities": recent_activities,
            }

    def get_low_stock_products(self) -> List[Product]:
        """Returns all products where current stock is at or below reorder level."""
        with self.manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products WHERE quantity <= reorder_level ORDER BY quantity ASC")
            rows = cursor.fetchall()
            return [Product.from_row(r) for r in rows]
