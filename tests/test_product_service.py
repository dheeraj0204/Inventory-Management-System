"""Tests for Product Management CRUD, SKU uniqueness, and Auto-complete search."""

import pytest
from app.utils.validators import ValidationError


class TestProductService:
    """Verifies complete product CRUD, auto ID generation, and constraint handling."""

    def test_create_valid_product(self, test_product_service, test_audit_service):
        data = {
            "name": "Precision Level Gauge",
            "category": "Electronics",
            "sku": "ELEC-LVL-99",
            "quantity": 12,
            "unit_price": 420.00,
            "reorder_level": 4,
            "supplier_name": "Apex Metrology",
        }
        product = test_product_service.create_product(data, change_reason="Test creation")
        assert product is not None
        assert product.product_id.startswith("PRD-")
        assert product.name == "Precision Level Gauge"
        assert product.quantity == 12
        assert product.total_valuation == 5040.00

        # Verify audit log was created
        logs = test_audit_service.get_audit_logs(entity_id=product.product_id, action_filter="CREATE")
        assert len(logs) == 1
        assert logs[0].entity_id == product.product_id

    def test_duplicate_sku_rejected(self, test_product_service):
        # Initial seed includes "ELEC-CAL-01"
        dup_data = {
            "name": "Another Caliper",
            "category": "Electronics",
            "sku": "ELEC-CAL-01",  # Duplicate SKU
            "quantity": 5,
            "unit_price": 100.0,
            "reorder_level": 2,
            "supplier_name": "Supplier X",
        }
        with pytest.raises(ValidationError) as exc:
            test_product_service.create_product(dup_data)
        assert "already in use" in exc.value.message.lower()

    def test_get_product_by_id(self, test_product_service):
        product = test_product_service.get_product_by_id("PRD-1001")
        assert product is not None
        assert product.name == "Precision Digital Caliper"

    def test_update_product(self, test_product_service, test_audit_service):
        update_data = {
            "name": "Precision Digital Caliper Pro",
            "category": "Electronics",
            "sku": "ELEC-CAL-01",
            "quantity": 40,  # Changed from 35 to 40
            "unit_price": 1300.00,
            "reorder_level": 10,
            "supplier_name": "Apex Metrology Labs",
        }
        updated = test_product_service.update_product("PRD-1001", update_data, change_reason="Upgraded model")
        assert updated.name == "Precision Digital Caliper Pro"
        assert updated.quantity == 40
        assert updated.unit_price == 1300.00

        # Verify audit log recorded UPDATE with diff
        logs = test_audit_service.get_audit_logs(action_filter="UPDATE")
        latest = [l for l in logs if l.entity_id == "PRD-1001"][0]
        assert latest.action == "UPDATE"
        new_dict = latest.get_new_dict()
        assert new_dict["name"] == "Precision Digital Caliper Pro"

    def test_delete_product(self, test_product_service, test_audit_service):
        # Create a product to delete
        data = {
            "name": "Disposable Lab Wipes",
            "category": "Stationery",
            "sku": "STAT-WIP-88",
            "quantity": 100,
            "unit_price": 15.00,
            "reorder_level": 10,
            "supplier_name": "SafeTech",
        }
        created = test_product_service.create_product(data)
        pid = created.product_id

        # Delete product
        result = test_product_service.delete_product(pid, reason="End of lifecycle")
        assert result is True

        # Verify it no longer exists
        assert test_product_service.get_product_by_id(pid) is None

        # Verify audit log retains DELETE event
        logs = test_audit_service.get_audit_logs(action_filter="DELETE")
        matching = [l for l in logs if l.entity_id == pid]
        assert len(matching) == 1
        assert matching[0].action == "DELETE"

    def test_search_and_filter(self, test_product_service):
        # Filter by category
        stationery = test_product_service.get_all_products(category_filter="Stationery")
        assert len(stationery) >= 2
        for p in stationery:
            assert p.category == "Stationery"

        # Search query by SKU partial
        found = test_product_service.get_all_products(search_query="CAL-01")
        assert len(found) >= 1
        assert found[0].sku == "ELEC-CAL-01"

    def test_search_autocomplete(self, test_product_service):
        results = test_product_service.search_autocomplete("Caliper")
        assert len(results) >= 1
        assert "Precision Digital Caliper" in results[0]["display"]

        # Partial case insensitive
        results_lower = test_product_service.search_autocomplete("gloves")
        assert len(results_lower) >= 1
        assert "Anti-Static Cleanroom Gloves" in results_lower[0]["name"]
