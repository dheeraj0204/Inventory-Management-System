# Software Requirements Specification (SRS)

## Inventory Management System — Improving Data Accuracy Using Total Quality Management (Q07)

- **Student Name**: Dheeraj Khetwal
- **Course**: BBAT104 — Fundamentals of Total Quality Management
- **Academic Session**: 2026–27
- **Baseline System**: Inventory Management System
- **Assigned Quality Goal**: Q07 — Improve Data Accuracy
- **Version**: 1.0.0

---

## 1. Introduction & Executive Summary

### 1.1 Purpose
This Software Requirements Specification (SRS) details the functional and non-functional requirements for the desktop Inventory Management System developed for course **BBAT104**. The system serves as an operational proof-of-concept demonstrating how modern software engineering practices, relational database constraints, and Total Quality Management (TQM) statistical quality control methodologies resolve persistent data inaccuracies (Quality Goal **Q07**).

### 1.2 Scope
The application is a standalone desktop application built in Python 3 using CustomTkinter, SQLite3, and Matplotlib. It encompasses complete inventory catalog lifecycle management (CRUD), audited stock adjustments, transaction logging with JSON change diffs, and a dedicated TQM Quality & Analytics module incorporating Critical to Quality (CTQ) scorecards, defect checksheets, Pareto 80/20 analysis, Ishikawa (Fishbone) root cause diagrams, Failure Mode and Effects Analysis (FMEA), SIPOC process flows, and Plan-Do-Check-Act (PDCA) improvement logs.

---

## 2. Overall Description

### 2.1 Problem Statement (The "Cost of Poor Quality")
In legacy college and small-enterprise inventory software, data accuracy is compromised by:
1. **Unconstrained Text Input**: Typos in product names, negative numbers entered in quantities, and letters typed into currency fields.
2. **Category Fragmentation**: Inconsistent spelling (e.g., "Elec", "Electronic", "Electronics") that distorts financial reporting and category analytics.
3. **Identifier Duplication**: Accidental duplicate SKU assignment causing stock desynchronization and scan failures.
4. **Unaccounted Stock Variance**: Stock adjustments applied without documentation or audit trails.
5. **Accidental Deletions**: Destructive actions triggered without confirmation safeguards.

### 2.2 Quality Goal Q07 Objectives
The primary quality objective is **Zero Data Entry Defects** achieved through proactive prevention (poka-yoke) rather than reactive cleanup:
- **Poka-Yoke Input Gates**: Reject malformed inputs before reaching the persistence tier.
- **Controlled Taxonomies**: Standardize categories through immutable master dropdowns.
- **Traceability**: Maintain a 100% complete, immutable audit trail for all catalog and inventory events.
- **Statistical Quality Control**: Monitor operational defect trends using Pareto charts and FMEA risk scores.

---

## 3. Specific Functional Requirements

### 3.1 Module A: Dashboard & Analytics
- **FR-D1**: Display live unique product counts, total stock units, inventory valuation, and low-stock count from SQLite.
- **FR-D2**: Formula for valuation: $\text{Total Valuation} = \sum (\text{Product Quantity} \times \text{Unit Price})$.
- **FR-D3**: Render embedded Matplotlib category valuation breakdown bar chart.
- **FR-D4**: Render real-time feed of the 6 most recent audit events with action badges.
- **FR-D5**: Provide quick action buttons to navigate directly to product registration and stock adjustments.

### 3.2 Module B: Product Management (CRUD)
- **FR-P1 (Create)**: Generate unique product identifiers (`PRD-1001`, `PRD-1002`).
- **FR-P2 (Input Masking)**: Validate name (2–100 chars), category (controlled list), SKU (`^[A-Z0-9-]{3,20}$`), quantity (integer $\ge 0$), price (float $> 0.00$), reorder level (integer $\ge 0$), supplier (2–100 chars).
- **FR-P3 (Read)**: Display products in a responsive table with search and category filtering.
- **FR-P4 (Update)**: Allow editing existing products with transactional JSON diff logging.
- **FR-P5 (Delete)**: Mandate explicit confirmation modal with product impact summary.

### 3.3 Module C: Inventory & Stock Management
- **FR-I1 (Stock Availability)**: Real-time stock status flags (`OPTIMAL`, `REORDER`, `CRITICAL`).
- **FR-I2 (Stock Adjustment)**: Support audited stock adjustments requiring non-empty reasons and non-negative counts.
- **FR-I3 (Variance Calculation)**: Display live preview of quantity variance ($+$ or $-$ units).
- **FR-I4 (Movement History)**: Record discrete movement rows (`IN`, `OUT`, `ADJUSTMENT`, `INITIAL`) with timestamps.

### 3.4 Module D: Mandatory Q07 Quality Features
- **FR-Q1 (Feature 1 - Input Masking)**: Strict client-side and service-tier validation. Rejection of negative numbers, invalid strings, and malformed SKUs.
- **FR-Q2 (Feature 2 - Dropdowns)**: Restrict category assignment to controlled list: `Electronics`, `Stationery`, `Furniture`, `Accessories`, `Raw Materials`, `Other`.
- **FR-Q3 (Feature 3 - Auto-complete)**: Real-time debounced suggestion dropdown matching database records by SKU or name.
- **FR-Q4 (Feature 4 - Confirmation Modals)**: CustomTkinter modal dialogs for deletion and stock adjustments with structured impact summaries.
- **FR-Q5 (Feature 5 - Audit Logging)**: Dedicated `audit_logs` table recording `CREATE`, `UPDATE`, `DELETE`, and `STOCK_ADJUSTMENT` with JSON serialized old and new values.

### 3.5 Module E: TQM Quality Management Suite
- **FR-T1 (CTQ Scorecard)**: Compute dynamic compliance percentages for Quantity Accuracy, SKU Uniqueness, Field Completeness, Category Standardization, and Audit Traceability.
- **FR-T2 (Defect Checksheet)**: Record defect codes, categories, severity, frequency, corrective actions, and resolution statuses.
- **FR-T3 (Pareto Analysis)**: Matplotlib dual-axis chart plotting sorted defect frequencies and cumulative percentage curve with an 80% reference cutoff line.
- **FR-T4 (Fishbone Diagram)**: Document and visualize root causes across People, Process, Software Code, and Infrastructure.
- **FR-T5 (FMEA Worksheet)**: Calculate Risk Priority Number ($RPN = \text{Severity} \times \text{Occurrence} \times \text{Detection}$) on a 1–10 scale.
- **FR-T6 (SIPOC Process Map)**: Flow matrix detailing Suppliers, Inputs, Process Steps, Outputs, and Customers.
- **FR-T7 (PDCA Tracker)**: Track Plan-Do-Check-Act continuous improvement cycles across 4 distinct stages.

---

## 4. Non-Functional Requirements

### 4.1 Data Integrity & ACID Compliance
- SQLite database configured with `PRAGMA foreign_keys = ON;`, `PRAGMA journal_mode = WAL;`, and atomic context manager transactions.

### 4.2 Usability & UI/UX Standards
- Enterprise Dark Navy sidebar (`#0F172A`) with light neutral main canvas (`#F8FAFC`).
- Consistent typography (Segoe UI), rounded corner radii, and accessible status colors.

### 4.3 Performance
- Query debouncing (180ms) on auto-complete search.
- Instant table rendering for catalog sizes up to 10,000 items through indexed queries.

### 4.4 Portability & Dependencies
- Pure Python 3 desktop execution on Windows without web server or browser dependencies.
