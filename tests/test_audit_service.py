"""Tests for Audit Logging (Q07 Feature 5) and Transaction Rollback Safety."""

import pytest
import sqlite3
from app.utils.validators import ValidationError


class TestAuditService:
    """Verifies audit logging integrity, JSON formatting, and database transaction safety."""

    def test_audit_logs_contain_json_diffs(self, test_product_service, test_audit_service):
        data = {
            "name": "Audit Test Gauge",
            "category": "Electronics",
            "sku": "AUD-TST-01",
            "quantity": 10,
            "unit_price": 50.0,
            "reorder_level": 2,
            "supplier_name": "Test Supplier",
        }
        prod = test_product_service.create_product(data, change_reason="Audit test creation")

        # Update product
        update_data = {
            "name": "Audit Test Gauge Renamed",
            "category": "Electronics",
            "sku": "AUD-TST-01",
            "quantity": 15,
            "unit_price": 55.0,
            "reorder_level": 2,
            "supplier_name": "Test Supplier",
        }
        test_product_service.update_product(prod.product_id, update_data, change_reason="Price change")

        # Check audit entry
        logs = test_audit_service.get_audit_logs(action_filter="UPDATE")
        update_log = [l for l in logs if l.entity_id == prod.product_id][0]

        old_dict = update_log.get_old_dict()
        new_dict = update_log.get_new_dict()

        assert old_dict["name"] == "Audit Test Gauge"
        assert new_dict["name"] == "Audit Test Gauge Renamed"
        assert old_dict["quantity"] == 10
        assert new_dict["quantity"] == 15

    def test_database_transaction_rollback_on_failure(self, test_db_manager, test_product_service, test_audit_service):
        """Verifies ACID properties: transaction failure rolls back both data and audit rows."""
        initial_prod_count = len(test_product_service.get_all_products())
        initial_audit_count = len(test_audit_service.get_audit_logs())

        # Simulate an operation that encounters a mid-transaction failure
        with pytest.raises(sqlite3.IntegrityError):
            with test_db_manager.transaction() as conn:
                # 1. Insert product
                conn.execute(
                    """
                    INSERT INTO products (product_id, name, category, sku, quantity, unit_price, reorder_level, supplier_name, created_at, updated_at)
                    VALUES ('PRD-FAIL-1', 'Fail Product', 'Electronics', 'FAIL-SKU-1', 10, 20.0, 5, 'Fail Supplier', 'now', 'now')
                    """
                )
                # 2. Trigger check constraint violation (negative stock in movement)
                conn.execute(
                    """
                    INSERT INTO stock_movements (product_id, movement_type, quantity_change, previous_quantity, new_quantity, reason, timestamp)
                    VALUES ('PRD-FAIL-1', 'OUT', -20, 10, -10, 'Illegal negative stock', 'now')
                    """
                )

        # After rollback, product count and audit count must remain exactly as before
        final_prod_count = len(test_product_service.get_all_products())
        final_audit_count = len(test_audit_service.get_audit_logs())

        assert final_prod_count == initial_prod_count
        assert final_audit_count == initial_audit_count
        assert test_product_service.get_product_by_id("PRD-FAIL-1") is None
