"""Tests for Inventory Management, Stock Adjustments, and Valuation."""

import pytest
from app.utils.validators import ValidationError


class TestInventoryService:
    """Verifies stock adjustment transactions, movement logging, and formula calculations."""

    def test_adjust_stock_positive(self, test_inventory_service, test_product_service, test_audit_service):
        prod = test_product_service.get_product_by_id("PRD-1001")
        initial_qty = prod.quantity

        movement = test_inventory_service.adjust_stock(
            product_id="PRD-1001",
            new_quantity=initial_qty + 10,
            reason="Supplier restocking audit",
        )
        assert movement.movement_type == "IN"
        assert movement.quantity_change == 10
        assert movement.previous_quantity == initial_qty
        assert movement.new_quantity == initial_qty + 10

        # Verify product quantity updated in DB
        updated = test_product_service.get_product_by_id("PRD-1001")
        assert updated.quantity == initial_qty + 10

        # Verify audit log created
        logs = test_audit_service.get_audit_logs(action_filter="STOCK_ADJUSTMENT")
        assert len(logs) >= 1
        assert logs[0].entity_id == "PRD-1001"

    def test_adjust_stock_negative(self, test_inventory_service, test_product_service):
        prod = test_product_service.get_product_by_id("PRD-1002")
        initial_qty = prod.quantity

        movement = test_inventory_service.adjust_stock(
            product_id="PRD-1002",
            new_quantity=initial_qty - 5,
            reason="Damaged items write-off",
        )
        assert movement.movement_type == "OUT"
        assert movement.quantity_change == -5
        assert movement.new_quantity == initial_qty - 5

    def test_adjust_stock_identical_quantity_raises_error(self, test_inventory_service, test_product_service):
        prod = test_product_service.get_product_by_id("PRD-1001")
        with pytest.raises(ValidationError) as exc:
            test_inventory_service.adjust_stock(
                product_id="PRD-1001",
                new_quantity=prod.quantity,
                reason="Redundant entry",
            )
        assert "identical" in exc.value.message.lower()

    def test_adjust_stock_negative_quantity_raises_error(self, test_inventory_service):
        with pytest.raises(ValidationError) as exc:
            test_inventory_service.adjust_stock(
                product_id="PRD-1001",
                new_quantity=-10,
                reason="Invalid adjustment",
            )
        assert "cannot be negative" in exc.value.message.lower()

    def test_inventory_summary_valuation_formula(self, test_inventory_service):
        summary = test_inventory_service.get_inventory_summary()
        assert summary["total_products"] == 10
        assert summary["total_units"] > 0
        assert summary["total_valuation"] > 0.0
        assert "category_breakdown" in summary
        assert len(summary["category_breakdown"]) > 0

    def test_low_stock_identification(self, test_inventory_service):
        # Initial seed includes PRD-1004 (Microscope, qty 4, reorder 5) and PRD-1010 (Weight set, qty 3, reorder 5)
        low_stock = test_inventory_service.get_low_stock_products()
        assert len(low_stock) >= 2
        for p in low_stock:
            assert p.quantity <= p.reorder_level
