# Known Limitations & Engineering Assumptions

## Inventory Management System — TQM Q07 Project

- **Student**: Dheeraj Khetwal
- **Course**: BBAT104 — Fundamentals of Total Quality Management
- **Academic Session**: 2026–27

---

## 1. Scope & Academic Context

In accordance with academic integrity and software engineering best practices, this document transparently records the design boundaries, known architectural limitations, and assumptions of the system. This project is developed as an educational, production-grade proof-of-concept for **BBAT104: Fundamentals of Total Quality Management**, specifically demonstrating **Quality Goal Q07 (Improve Data Accuracy)**.

---

## 2. Technical Limitations

### 2.1 Single-User Local Execution
- **Limitation**: The application is architected as a standalone desktop application. It does not provide multi-tenant software-as-a-service (SaaS) features or cloud session management.
- **Rationale**: The project requirements mandate a native Python desktop GUI running locally on Windows via Visual Studio Code without web server overhead.
- **Engineering Reality**: The system does not falsely claim to offer enterprise-grade OAuth2, LDAP, or multi-user Role-Based Access Control (RBAC).

### 2.2 Concurrency & Database Engine
- **Limitation**: SQLite is an embedded, file-based database engine. While Write-Ahead Logging (`WAL` mode) is enabled to support concurrent read transactions, concurrent write transactions are serialized via database table locks.
- **Impact**: Suitable for single workstations or small storekeeper terminals; not designed for high-throughput distributed warehouse clusters exceeding hundreds of concurrent write queries per second.

### 2.3 Barcode Scanner Hardware Interface
- **Limitation**: The system accepts barcode input via standard **Keyboard Wedge emulation** (where USB/Bluetooth 1D/2D scanners type directly into the focused SKU entry field). It does not interface directly with proprietary RS-232 serial COM port drivers.
- **Mitigation**: Standard commercial handheld barcode scanners support HID keyboard emulation by default, functioning seamlessly with the application's auto-capitalizing SKU input fields.

### 2.4 Reporting Export Formats
- **Limitation**: Reports, Pareto charts, and CTQ scorecards are rendered dynamically in GUI tables and embedded Matplotlib canvas figures. Direct native one-click export to PDF and Excel (.xlsx) is currently not implemented to avoid bloated third-party dependencies (e.g., ReportLab, openpyxl).
- **Workaround**: Data can be queried directly from the SQLite database (`data/inventory_tqm.db`) using Python scripts or standard SQLite browser tools.

---

## 3. Recommended Future Enhancements

1. **Multi-Warehouse Transfers**: Extend the database schema to support multiple warehouse locations (`warehouse_id`) and inter-depot transfer orders.
2. **Automated Purchase Order EDI**: Integrate REST API connectors with authorized suppliers to automatically transmit electronic Purchase Orders when stock reaches the reorder threshold.
3. **Role-Based Login**: Implement role-based credentials distinguishing Receiving Clerks (data entry), Store Supervisors (stock adjustment approvals), and Quality Auditors (view-only analytics).
