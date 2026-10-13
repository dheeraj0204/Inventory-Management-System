"""Services package initialization."""
from app.services.product_service import ProductService
from app.services.inventory_service import InventoryService
from app.services.audit_service import AuditService
from app.services.tqm_service import TQMService

product_service = ProductService()
inventory_service = InventoryService()
audit_service = AuditService()
tqm_service = TQMService()

__all__ = [
    "ProductService",
    "InventoryService",
    "AuditService",
    "TQMService",
    "product_service",
    "inventory_service",
    "audit_service",
    "tqm_service",
]
