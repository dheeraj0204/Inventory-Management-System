"""Pytest configuration and isolated database fixtures."""

import pytest
from pathlib import Path
from app.database.connection import DatabaseManager
from app.database.schema import initialize_database
from app.services.product_service import ProductService
from app.services.inventory_service import InventoryService
from app.services.audit_service import AuditService
from app.services.tqm_service import TQMService


@pytest.fixture
def test_db_manager(tmp_path: Path):
    """Provides an isolated SQLite database manager for automated tests."""
    db_file = tmp_path / "test_inventory_tqm.db"
    manager = DatabaseManager(db_file)
    initialize_database(manager)
    return manager


@pytest.fixture
def test_product_service(test_db_manager):
    return ProductService(test_db_manager)


@pytest.fixture
def test_inventory_service(test_db_manager):
    return InventoryService(test_db_manager)


@pytest.fixture
def test_audit_service(test_db_manager):
    return AuditService(test_db_manager)


@pytest.fixture
def test_tqm_service(test_db_manager):
    return TQMService(test_db_manager)
