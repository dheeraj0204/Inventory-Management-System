"""Data model representing a managed inventory product."""

from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional
import sqlite3


@dataclass
class Product:
    """Represents a product item in the inventory catalog."""
    product_id: str
    name: str
    category: str
    sku: str
    quantity: int
    unit_price: float
    reorder_level: int
    supplier_name: str
    created_at: str
    updated_at: str
    id: Optional[int] = None

    @property
    def total_valuation(self) -> float:
        """Returns total valuation for this stock line: Quantity * Unit Price."""
        return round(self.quantity * self.unit_price, 2)

    @property
    def is_low_stock(self) -> bool:
        """Determines if the product quantity is at or below reorder threshold."""
        return self.quantity <= self.reorder_level

    def to_dict(self) -> Dict[str, Any]:
        """Converts product instance to dictionary."""
        d = asdict(self)
        d["total_valuation"] = self.total_valuation
        d["is_low_stock"] = self.is_low_stock
        return d

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Product":
        """Instantiates Product from SQLite row object."""
        return cls(
            id=row["id"],
            product_id=row["product_id"],
            name=row["name"],
            category=row["category"],
            sku=row["sku"],
            quantity=int(row["quantity"]),
            unit_price=float(row["unit_price"]),
            reorder_level=int(row["reorder_level"]),
            supplier_name=row["supplier_name"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
