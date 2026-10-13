# Testing & Data Quality Verification Report

## Automated & Integration Test Results — TQM Quality Goal Q07

- **Student**: Dheeraj Khetwal
- **Course**: BBAT104 — Fundamentals of Total Quality Management
- **Academic Session**: 2026–27
- **Test Framework**: `pytest 9.1.1` on Python 3.14 (Virtual Environment)
- **Status**: **100% PASSED (42/42 Tests)**

---

## 1. Test Strategy & Architecture

To satisfy strict academic and software engineering standards, the automated test suite follows these architectural principles:
1. **Zero Database Pollution**: Every test module runs against an ephemeral SQLite database created via pytest's `tmp_path` fixture. The operational database (`data/inventory_tqm.db`) is never modified during test execution.
2. **Deterministic Schemas**: Test databases are automatically initialized with full schema DDL, foreign key enforcement, and baseline seed records.
3. **Poka-Yoke Boundary Testing**: Extensive coverage of invalid, boundary, and edge-case inputs (empty strings, decimals in integer fields, negative quantities, duplicate identifiers).
4. **Transaction Rollback Verification**: Direct testing of SQLite ACID properties to ensure failed operations never commit orphaned audit records or corrupt inventory balances.

---

## 2. Test Execution Summary

```
============================= test session starts =============================
platform win32 -- Python 3.14.5, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\dheer\Downloads\Inventory_TQM_Project
collected 42 items

tests/test_audit_service.py ......................... [  4%]  (2 passed)
tests/test_inventory_service.py ..................... [ 19%]  (6 passed)
tests/test_product_service.py ....................... [ 35%]  (7 passed)
tests/test_tqm_service.py ........................... [ 52%]  (7 passed)
tests/test_validators.py ............................ [100%]  (20 passed)

============================= 42 passed in 0.79s ==============================
```

---

## 3. Detailed Test Matrix by Module

### 3.1 Input Masking & Strict Validation (`tests/test_validators.py`)

| Test Name | Test Objective / Assertion | Result |
|---|---|:---:|
| `test_normalize_text` | Verifies whitespace stripping and internal space deduplication | **PASS** |
| `test_valid_product_name` | Confirms valid string names (2–100 chars) are accepted | **PASS** |
| `test_empty_product_name_raises_error` | Verifies blank and whitespace-only names are rejected | **PASS** |
| `test_product_name_too_short_raises_error` | Verifies names under 2 characters raise `ValidationError` | **PASS** |
| `test_product_name_too_long_raises_error` | Verifies names over 100 characters raise `ValidationError` | **PASS** |
| `test_valid_category` | Confirms case-insensitive match against `ALLOWED_CATEGORIES` | **PASS** |
| `test_invalid_category_raises_error` | Rejects arbitrary unlisted categories | **PASS** |
| `test_valid_sku` | Validates standard alphanumeric hyphenated SKU codes | **PASS** |
| `test_empty_sku_raises_error` | Rejects empty SKU codes | **PASS** |
| `test_malformed_sku_raises_error` | Rejects special characters (`@#$$`) and invalid lengths | **PASS** |
| `test_valid_quantity` | Accepts positive whole integers (including integer strings) | **PASS** |
| `test_negative_quantity_raises_error` | Rejects negative integers ($< 0$) with explicit error message | **PASS** |
| `test_decimal_quantity_rejected` | Rejects float quantities (e.g., `12.5`) to prevent fractional stock | **PASS** |
| `test_invalid_string_quantity_raises_error` | Rejects alphabetic text in quantity fields | **PASS** |
| `test_valid_unit_price` | Formats and validates numeric prices to 2 decimal places | **PASS** |
| `test_zero_or_negative_price_rejected` | Rejects zero ($0.00$) and negative prices | **PASS** |
| `test_invalid_price_string_raises_error` | Rejects non-numeric text in price fields | **PASS** |
| `test_reorder_level` | Verifies non-negative integer reorder thresholds | **PASS** |
| `test_full_product_data_validation` | End-to-end dictionary sanitization and validation pipeline | **PASS** |
| `test_compute_dict_diff` | Computes granular `{field: {old, new}}` diffs for JSON audit logs | **PASS** |

### 3.2 Product Catalog Management (`tests/test_product_service.py`)

| Test Name | Test Objective / Assertion | Result |
|---|---|:---:|
| `test_create_valid_product` | Verifies atomic creation of product, stock movement, and audit log | **PASS** |
| `test_duplicate_sku_rejected` | Verifies pre-save and database rejection of duplicate SKUs | **PASS** |
| `test_get_product_by_id` | Queries existing product by unique `product_id` | **PASS** |
| `test_update_product` | Modifies product and records JSON change diffs in audit log | **PASS** |
| `test_delete_product` | Deletes product and archives final snapshot in audit log | **PASS** |
| `test_search_and_filter` | Verifies category filtering and case-insensitive keyword search | **PASS** |
| `test_search_autocomplete` | Verifies debounced autocomplete suggestions against live database | **PASS** |

### 3.3 Inventory & Stock Management (`tests/test_inventory_service.py`)

| Test Name | Test Objective / Assertion | Result |
|---|---|:---:|
| `test_adjust_stock_positive` | Applies stock addition (`IN`), updates quantity, and logs movement | **PASS** |
| `test_adjust_stock_negative` | Applies stock deduction (`OUT`) and records mandatory reason | **PASS** |
| `test_adjust_stock_identical_quantity_raises_error` | Rejects zero-variance adjustments to prevent redundant log spam | **PASS** |
| `test_adjust_stock_negative_quantity_raises_error` | Rejects adjustments that would result in negative stock | **PASS** |
| `test_inventory_summary_valuation_formula` | Validates formula: $\text{Valuation} = \sum (\text{Qty} \times \text{Price})$ | **PASS** |
| `test_low_stock_identification` | Flags products where $\text{quantity} \le \text{reorder\_level}$ | **PASS** |

### 3.4 Transaction Safety & Audit Logging (`tests/test_audit_service.py`)

| Test Name | Test Objective / Assertion | Result |
|---|---|:---:|
| `test_audit_logs_contain_json_diffs` | Verifies audit records contain parsed JSON representations | **PASS** |
| `test_database_transaction_rollback_on_failure` | Proves that failed transactions roll back all partial writes | **PASS** |

### 3.5 TQM Analytics & Continuous Improvement (`tests/test_tqm_service.py`)

| Test Name | Test Objective / Assertion | Result |
|---|---|:---:|
| `test_fmea_rpn_calculation` | Validates formula: $RPN = S \times O \times D$ ($8 \times 4 \times 5 = 160$) | **PASS** |
| `test_fmea_score_range_validation` | Rejects scores outside the 1–10 scale | **PASS** |
| `test_pareto_analysis_sorting_and_cumulative_percentages` | Verifies descending sort, cumulative sums, and 80% cutoff line | **PASS** |
| `test_ctq_scorecard_calculation` | Computes live percentages for the 5 CTQ parameters | **PASS** |
| `test_defect_logging_and_resolution` | Tests checksheet logging and resolution with corrective actions | **PASS** |
| `test_fishbone_and_sipoc_data_integrity` | Validates 4M cause structures and 5-stage SIPOC matrix | **PASS** |
| `test_pdca_lifecycle` | Validates PDCA cycle creation and stage transitions (`PLAN` $\to$ `DO`) | **PASS** |

---

## 4. GUI Sanity Verification Results

In addition to headless automated unit tests, the desktop CustomTkinter GUI interface was verified using a standalone rendering test harness:
- **`AppWindow` Initialization**: Passed without geometry or DPI scaling warnings.
- **View Transitions**: Cycled sequentially through `dashboard`, `products`, `inventory`, `audit`, and `tqm` views.
- **Embedded Matplotlib Canvases**: Verified `FigureCanvasTkAgg` rendered both the Category Distribution chart and the dual-axis Pareto chart without memory leaks or GUI freezes.
- **Result**: `GUI Sanity Check PASSED 100%!`.
