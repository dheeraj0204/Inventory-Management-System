# SIPOC Process Map: Inventory Lifecycle Management

## Total Quality Management (TQM) — Quality Goal Q07 (Improve Data Accuracy)

- **Student**: Dheeraj Khetwal
- **Course**: BBAT104 — Fundamentals of Total Quality Management
- **Academic Session**: 2026–27

---

## 1. Executive Summary & Purpose

In Total Quality Management (TQM), a **SIPOC** (Suppliers, Inputs, Process, Outputs, Customers) diagram is a high-level process mapping tool used to define the boundaries of an operational workflow before implementing process improvements.

For **Quality Goal Q07 (Improve Data Accuracy)**, the SIPOC map identifies exactly where inventory data enters the system, which actors supply the information, what transforms that data, and how corrupted inputs cause downstream operational failure.

---

## 2. High-Level Process Flow Diagram

```mermaid
graph LR
    S[Suppliers<br/>Vendors / Clerks] -->|Invoices, Goods, SKUs| I[Inputs<br/>Item Data & Counts]
    I --> P[Process<br/>5-Stage Inventory Lifecycle]
    P --> O[Outputs<br/>Audited Stock & Reports]
    O --> C[Customers<br/>Production, Finance, Audits]
```

---

## 3. Comprehensive SIPOC Matrix

| Stage | Suppliers | Inputs | Process Steps (Key TQM Controls) | Outputs | Customers |
|---|---|---|---|---|---|
| **1. Receiving** | Equipment Vendors, Distributors, Freight Carriers | Delivery Challan, Purchase Order, Physical Goods, Supplier Batch Labels | **Goods Inward & Physical Verification**<br>• Count delivered packages<br>• Match PO number against physical packing slip<br>• Inspect carton condition | Verified Goods Delivery Note (GDN), Physical Inventory Cartons | Warehouse Receiving Clerks, Quality Inspection Dept. |
| **2. Registration (Q07 Focus)** | Receiving Clerks, Data Entry Operators | Physical item specifications, Catalog descriptions, Vendor model # | **Catalog Registration (Input Masking)**<br>• Validate product title & supplier<br>• Select category from controlled dropdown (Poka-Yoke)<br>• Validate uppercase SKU format<br>• Enforce non-negative quantity & price $> 0.00$ | Validated Product Record, Unique System ID (`PRD-xxxx`), Barcode Master | Enterprise Inventory Database, Warehouse Floor Staff |
| **3. Warehousing** | Warehouse Supervisors, Forklift Operators | Validated Product Record, Warehouse Bin Location Map | **Storage & Stock Allocation**<br>• Place items in assigned bins<br>• Associate physical rack with system record<br>• Maintain ambient temperature/ESD storage rules | Updated Stock Location Index, Accessible Bin Inventory | Storekeepers, Material Handling Teams |
| **4. Issue & Adjustment** | Production Supervisors, Internal Requisitioners | Material Requisition Note (MRN), Damage Reports, Cycle Count Sheets | **Stock Issue & Audited Adjustment**<br>• Verify requested SKU via Auto-complete<br>• Check available stock balance<br>• If count mismatch, perform audited stock adjustment with mandatory reason<br>• Require confirmation modal | Deducted Stock Ledger, Movement Record (`IN`/`OUT`/`ADJUSTMENT`), JSON Audit Log | Assembly Lines, Packaging Units, Maintenance Crews |
| **5. Quality Audit & Analytics** | Internal Quality Auditor, TQM Committee | Relational Database Records, Transaction Logs, Defect Checksheets | **Quality Analysis & Continuous Improvement**<br>• Calculate live CTQ compliance metrics<br>• Aggregate defect checksheets by category<br>• Plot Pareto 80/20 frequency chart<br>• Update FMEA worksheet & calculate RPN<br>• Advance PDCA continuous improvement cycle | Executive Dashboard KPIs, Pareto Chart, FMEA Risk Scorecard, PDCA Action Plan | Plant Management, Financial Controllers, TQM Committee |

---

## 4. Analysis: Where Inaccuracies Enter & How Q07 Mitigates Them

1. **At Step 2 (Registration)**:
   - *Failure Mode*: Operator keys in unstandardized category name (e.g. "elec", "Electronic") or negative stock.
   - *Q07 Solution*: Feature 1 (Input Masking & Range Checks) and Feature 2 (Controlled Dropdowns) block invalid entries immediately at the form tier.
2. **At Step 4 (Issue & Adjustment)**:
   - *Failure Mode*: Operator adjusts stock to fix a count error without documenting the cause or approving the variance.
   - *Q07 Solution*: Feature 4 (Confirmation Dialogs) and Feature 5 (Audit Logging) enforce documented reasons and store full JSON before/after state diffs.
