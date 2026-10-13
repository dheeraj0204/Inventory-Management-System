"""Input masking, normalization, and strict validation engine (Q07 Feature 1 & 2)."""

import re
from typing import Any, Dict, Optional, Tuple
from app.config import ALLOWED_CATEGORIES


class ValidationError(Exception):
    """Custom exception raised when data validation fails."""

    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.field = field

    def to_dict(self) -> Dict[str, str]:
        return {"field": self.field or "general", "error": self.message}


class ProductValidator:
    """Strict validator enforcing Q07 data accuracy standards."""

    SKU_REGEX = re.compile(r"^[A-Z0-9]{2,10}(?:-[A-Z0-9]{1,10})*$", re.IGNORECASE)

    @staticmethod
    def normalize_text(value: Any) -> str:
        """Strip whitespace and collapse multiple internal spaces."""
        if value is None:
            return ""
        s = str(value).strip()
        return re.sub(r"\s+", " ", s)

    @classmethod
    def validate_product_name(cls, name: Any) -> str:
        """Validates product name: required, length 2-100 characters."""
        cleaned = cls.normalize_text(name)
        if not cleaned:
            raise ValidationError("Product name is mandatory and cannot be empty.", field="name")
        if len(cleaned) < 2:
            raise ValidationError("Product name must be at least 2 characters long.", field="name")
        if len(cleaned) > 100:
            raise ValidationError("Product name cannot exceed 100 characters.", field="name")
        return cleaned

    @classmethod
    def validate_category(cls, category: Any) -> str:
        """Validates category against strict controlled list (Q07 Feature 2)."""
        cleaned = cls.normalize_text(category)
        if not cleaned:
            raise ValidationError("Category selection is required.", field="category")

        # Case-insensitive match against allowed categories
        matched = next((c for c in ALLOWED_CATEGORIES if c.lower() == cleaned.lower()), None)
        if not matched:
            raise ValidationError(
                f"Invalid category '{cleaned}'. Must be one of: {', '.join(ALLOWED_CATEGORIES)}.",
                field="category",
            )
        return matched

    @classmethod
    def validate_sku(cls, sku: Any) -> str:
        """Validates SKU format: uppercase alphanumeric with hyphens, 3-20 chars."""
        cleaned = cls.normalize_text(sku).upper()
        if not cleaned:
            raise ValidationError("SKU code is mandatory.", field="sku")
        if len(cleaned) < 3 or len(cleaned) > 20:
            raise ValidationError("SKU must be between 3 and 20 characters in length.", field="sku")
        if not cls.SKU_REGEX.match(cleaned):
            raise ValidationError(
                "Invalid SKU format. Use uppercase alphanumeric characters optionally separated by hyphens (e.g., 'ELEC-101', 'LAPTOP-PRO').",
                field="sku",
            )
        return cleaned

    @classmethod
    def validate_quantity(cls, qty: Any) -> int:
        """Strict integer parsing: rejects floats, strings with decimals, negative numbers."""
        if qty is None:
            raise ValidationError("Quantity cannot be empty.", field="quantity")

        if isinstance(qty, bool):
            raise ValidationError("Invalid quantity type.", field="quantity")

        if isinstance(qty, int):
            parsed_qty = qty
        else:
            s_val = str(qty).strip()
            if not s_val:
                raise ValidationError("Quantity cannot be empty.", field="quantity")
            if not re.match(r"^-?\d+$", s_val):
                raise ValidationError(
                    f"Quantity must be a valid whole integer (received '{s_val}'). Decimal or non-numeric values are rejected.",
                    field="quantity",
                )
            try:
                parsed_qty = int(s_val)
            except ValueError:
                raise ValidationError(f"Invalid integer value for quantity: {s_val}", field="quantity")

        if parsed_qty < 0:
            raise ValidationError("Quantity cannot be negative. Must be >= 0.", field="quantity")
        if parsed_qty > 10_000_000:
            raise ValidationError("Quantity exceeds realistic maximum threshold (10,000,000).", field="quantity")

        return parsed_qty

    @classmethod
    def validate_unit_price(cls, price: Any) -> float:
        """Strict price parsing: non-negative, must be positive (> 0.0), max 2 decimal places."""
        if price is None:
            raise ValidationError("Unit price cannot be empty.", field="unit_price")

        if isinstance(price, bool):
            raise ValidationError("Invalid price type.", field="unit_price")

        try:
            val = float(price)
        except (ValueError, TypeError):
            raise ValidationError(
                f"Unit price must be a valid numeric amount (received '{price}').",
                field="unit_price",
            )

        if val <= 0:
            raise ValidationError("Unit price must be strictly greater than 0.00.", field="unit_price")
        if val > 1_000_000_000:
            raise ValidationError("Unit price exceeds maximum allowable threshold.", field="unit_price")

        # Standardize to 2 decimal places
        return round(val, 2)

    @classmethod
    def validate_reorder_level(cls, level: Any) -> int:
        """Validates reorder level: non-negative integer."""
        if level is None or str(level).strip() == "":
            return 5  # default

        if isinstance(level, bool):
            raise ValidationError("Invalid reorder level type.", field="reorder_level")

        if isinstance(level, int):
            parsed = level
        else:
            s_val = str(level).strip()
            if not re.match(r"^-?\d+$", s_val):
                raise ValidationError(
                    f"Reorder level must be a whole non-negative integer (received '{s_val}').",
                    field="reorder_level",
                )
            try:
                parsed = int(s_val)
            except ValueError:
                raise ValidationError(f"Invalid integer value for reorder level: {s_val}", field="reorder_level")

        if parsed < 0:
            raise ValidationError("Reorder level cannot be negative.", field="reorder_level")
        return parsed

    @classmethod
    def validate_supplier_name(cls, supplier: Any) -> str:
        """Validates supplier name: required, length 2-100 characters."""
        cleaned = cls.normalize_text(supplier)
        if not cleaned:
            raise ValidationError("Supplier name is required.", field="supplier_name")
        if len(cleaned) < 2 or len(cleaned) > 100:
            raise ValidationError("Supplier name must be between 2 and 100 characters.", field="supplier_name")
        return cleaned

    @classmethod
    def validate_product_data(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Runs full validation pipeline over product dictionary and returns sanitized data."""
        errors = {}
        validated = {}

        try:
            validated["name"] = cls.validate_product_name(data.get("name"))
        except ValidationError as e:
            errors["name"] = e.message

        try:
            validated["category"] = cls.validate_category(data.get("category"))
        except ValidationError as e:
            errors["category"] = e.message

        try:
            validated["sku"] = cls.validate_sku(data.get("sku"))
        except ValidationError as e:
            errors["sku"] = e.message

        try:
            validated["quantity"] = cls.validate_quantity(data.get("quantity"))
        except ValidationError as e:
            errors["quantity"] = e.message

        try:
            validated["unit_price"] = cls.validate_unit_price(data.get("unit_price"))
        except ValidationError as e:
            errors["unit_price"] = e.message

        try:
            validated["reorder_level"] = cls.validate_reorder_level(data.get("reorder_level", 5))
        except ValidationError as e:
            errors["reorder_level"] = e.message

        try:
            validated["supplier_name"] = cls.validate_supplier_name(data.get("supplier_name"))
        except ValidationError as e:
            errors["supplier_name"] = e.message

        if errors:
            first_key = next(iter(errors))
            raise ValidationError(
                f"Validation failed: {errors[first_key]} (Total errors: {len(errors)})",
                field=first_key,
            )

        return validated


def compute_dict_diff(old_dict: Dict[str, Any], new_dict: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Calculates granular changes between two dictionaries for auditable JSON logging."""
    diff = {}
    all_keys = set(old_dict.keys()).union(set(new_dict.keys()))
    ignore_keys = {"created_at", "updated_at", "id"}

    for key in all_keys:
        if key in ignore_keys:
            continue
        old_val = old_dict.get(key)
        new_val = new_dict.get(key)
        if old_val != new_val:
            diff[key] = {
                "old": old_val,
                "new": new_val,
            }
    return diff
