"""Tests for Input Masking, Normalization, and Strict Validation (Q07 Feature 1 & 2)."""

import pytest
from app.utils.validators import ProductValidator, ValidationError, compute_dict_diff


class TestProductValidators:
    """Tests all field-level and dictionary validation rules."""

    def test_normalize_text(self):
        assert ProductValidator.normalize_text("   Digital   Caliper  ") == "Digital Caliper"
        assert ProductValidator.normalize_text(None) == ""
        assert ProductValidator.normalize_text("   ") == ""

    def test_valid_product_name(self):
        name = ProductValidator.validate_product_name("  Oscilloscope Probe  ")
        assert name == "Oscilloscope Probe"

    def test_empty_product_name_raises_error(self):
        with pytest.raises(ValidationError) as exc:
            ProductValidator.validate_product_name("   ")
        assert "mandatory" in exc.value.message.lower()

    def test_product_name_too_short_raises_error(self):
        with pytest.raises(ValidationError) as exc:
            ProductValidator.validate_product_name("A")
        assert "at least 2 characters" in exc.value.message.lower()

    def test_product_name_too_long_raises_error(self):
        long_name = "X" * 105
        with pytest.raises(ValidationError) as exc:
            ProductValidator.validate_product_name(long_name)
        assert "cannot exceed 100 characters" in exc.value.message.lower()

    def test_valid_category(self):
        cat = ProductValidator.validate_category("electronics")
        assert cat == "Electronics"
        cat2 = ProductValidator.validate_category("  Furniture  ")
        assert cat2 == "Furniture"

    def test_invalid_category_raises_error(self):
        with pytest.raises(ValidationError) as exc:
            ProductValidator.validate_category("Unregistered Category")
        assert "must be one of" in exc.value.message.lower()

    def test_valid_sku(self):
        sku = ProductValidator.validate_sku("elec-cal-01")
        assert sku == "ELEC-CAL-01"
        sku2 = ProductValidator.validate_sku("ABC-1234-XYZ")
        assert sku2 == "ABC-1234-XYZ"

    def test_empty_sku_raises_error(self):
        with pytest.raises(ValidationError) as exc:
            ProductValidator.validate_sku("")
        assert "mandatory" in exc.value.message.lower()

    def test_malformed_sku_raises_error(self):
        # Invalid characters
        with pytest.raises(ValidationError):
            ProductValidator.validate_sku("ELEC@#$$")
        # Too short
        with pytest.raises(ValidationError):
            ProductValidator.validate_sku("A")

    def test_valid_quantity(self):
        assert ProductValidator.validate_quantity(25) == 25
        assert ProductValidator.validate_quantity("100") == 100
        assert ProductValidator.validate_quantity(0) == 0

    def test_negative_quantity_raises_error(self):
        with pytest.raises(ValidationError) as exc:
            ProductValidator.validate_quantity(-5)
        assert "cannot be negative" in exc.value.message.lower()

    def test_decimal_quantity_rejected(self):
        with pytest.raises(ValidationError) as exc:
            ProductValidator.validate_quantity("12.5")
        assert "whole integer" in exc.value.message.lower()

    def test_invalid_string_quantity_raises_error(self):
        with pytest.raises(ValidationError):
            ProductValidator.validate_quantity("twenty")

    def test_valid_unit_price(self):
        assert ProductValidator.validate_unit_price(45.5) == 45.50
        assert ProductValidator.validate_unit_price("129.99") == 129.99
        assert ProductValidator.validate_unit_price("10") == 10.00

    def test_zero_or_negative_price_rejected(self):
        with pytest.raises(ValidationError) as exc:
            ProductValidator.validate_unit_price(0.0)
        assert "strictly greater than 0.00" in exc.value.message.lower()

        with pytest.raises(ValidationError) as exc:
            ProductValidator.validate_unit_price(-15.5)
        assert "strictly greater than 0.00" in exc.value.message.lower()

    def test_invalid_price_string_raises_error(self):
        with pytest.raises(ValidationError):
            ProductValidator.validate_unit_price("free")

    def test_reorder_level(self):
        assert ProductValidator.validate_reorder_level(10) == 10
        assert ProductValidator.validate_reorder_level("") == 5  # default
        assert ProductValidator.validate_reorder_level(None) == 5

        with pytest.raises(ValidationError):
            ProductValidator.validate_reorder_level(-1)

    def test_full_product_data_validation(self):
        raw_data = {
            "name": "  Thermal Camera  ",
            "category": "Electronics",
            "sku": "elec-thm-01",
            "quantity": "15",
            "unit_price": "850.50",
            "reorder_level": "3",
            "supplier_name": "  Sensor Corp  ",
        }
        validated = ProductValidator.validate_product_data(raw_data)
        assert validated["name"] == "Thermal Camera"
        assert validated["category"] == "Electronics"
        assert validated["sku"] == "ELEC-THM-01"
        assert validated["quantity"] == 15
        assert validated["unit_price"] == 850.50
        assert validated["reorder_level"] == 3
        assert validated["supplier_name"] == "Sensor Corp"

    def test_compute_dict_diff(self):
        old = {"name": "Old Name", "quantity": 10, "unit_price": 50.0, "created_at": "now"}
        new = {"name": "New Name", "quantity": 10, "unit_price": 55.0, "created_at": "now"}
        diff = compute_dict_diff(old, new)
        assert "name" in diff
        assert diff["name"] == {"old": "Old Name", "new": "New Name"}
        assert "unit_price" in diff
        assert diff["unit_price"] == {"old": 50.0, "new": 55.0}
        assert "quantity" not in diff  # identical
        assert "created_at" not in diff  # ignored key
