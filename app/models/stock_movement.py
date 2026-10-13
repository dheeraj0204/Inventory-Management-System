"""Data model representing a stock movement entry."""

from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional
import sqlite3


@dataclass
class StockMovement:
    """Represents a discrete stock transition (inward, outward, or adjustment)."""
    product_id: str
    movement_type: str
    quantity_change: int
    previous_quantity: int
    new_quantity: int
    reason: str
    timestamp: str
    id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Converts to dictionary representation."""
        return asdict(self)

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "StockMovement":
        """Instantiates StockMovement from SQLite row."""
        return cls(
            id=row["id"],
            product_id=row["product_id"],
            movement_type=row["movement_type"],
            quantity_change=int(row["quantity_change"]),
            previous_quantity=int(row["previous_quantity"]),
            new_quantity=int(row["new_quantity"]),
            reason=row["reason"],
            timestamp=row["timestamp"],
        )
