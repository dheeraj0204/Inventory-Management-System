"""Views package initialization."""
from app.ui.views.dashboard_view import DashboardView
from app.ui.views.products_view import ProductsView
from app.ui.views.inventory_view import InventoryView
from app.ui.views.audit_view import AuditView
from app.ui.views.tqm_view import TQMView
from app.ui.views.auth_view import AuthWindow

__all__ = ["DashboardView", "ProductsView", "InventoryView", "AuditView", "TQMView", "AuthWindow"]
