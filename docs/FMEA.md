# Failure Mode and Effects Analysis (FMEA)

## Inventory Data Accuracy Analysis — Quality Goal Q07

- **Student**: Dheeraj Khetwal
- **Course**: BBAT104 — Fundamentals of Total Quality Management
- **Academic Session**: 2026–27
- **FMEA Scope**: Inventory Data Acquisition, Processing, and Modification

---

## 1. Methodology & Mathematical Framework

Failure Mode and Effects Analysis (FMEA) is a systematic, proactive technique for identifying potential process failures before they occur, assessing their relative risk, and establishing preventive controls.

### 1.1 Risk Priority Number (RPN) Formula
The overall risk score for each failure mode is calculated using the standard formula:

$$\text{RPN} = \text{Severity (S)} \times \text{Occurrence (O)} \times \text{Detection (D)}$$

Where:
- **Severity (S)** ($1 \le S \le 10$): Evaluates the seriousness of the failure's effect on downstream processes and financial reporting.
- **Occurrence (O)** ($1 \le O \le 10$): Evaluates the frequency or likelihood of the cause generating the failure.
- **Detection (D)** ($1 \le D \le 10$): Evaluates the capability of existing controls to detect the error before it affects the database or external users ($1 = \text{certain detection}$, $10 = \text{completely undetectable}$).

### 1.2 Scoring Scale Criteria (1–10 Standard)

| Rating | Severity (S) Criteria | Occurrence (O) Frequency | Detection (D) Capability |
|---|---|---|---|
| **1–2 (Minor)**| Insignificant inconvenience; no data loss. | Extremely rare ($\le 1$ in 10,000 transactions). | Almost certain automatic system detection. |
| **3–4 (Low)**  | Minor reporting delay; easily self-corrected. | Low frequency (occasional isolated error). | High likelihood of detection via basic checks. |
| **5–6 (Medium)**| Incorrect category reports; skewed valuation. | Moderate frequency (occurs weekly). | Moderate detection; requires manual review. |
| **7–8 (High)** | Stock out of sync; wrong replenishment orders. | Repeated error pattern (occurs daily). | Poor detection; discovered only at annual audit. |
| **9–10 (Critical)**| Permanent data loss; critical production halt. | Very high frequency (routine daily failure). | Undetectable; enters database silently. |

### 1.3 Project Risk Classification Thresholds
- **High Risk**: $\text{RPN} \ge 200$ (Requires immediate architectural Poka-Yoke prevention).
- **Medium Risk**: $100 \le \text{RPN} < 200$ (Requires automated software validation rules).
- **Low Risk**: $\text{RPN} < 100$ (Standard operational controls sufficient).

---

## 2. Comprehensive FMEA Worksheet

Below is the verified FMEA worksheet showing the evaluation of failure modes in the baseline legacy system and the reduction in RPN achieved by the **Q07 TQM application**.

| ID | Process Step | Potential Failure Mode | Potential Failure Effect | Potential Cause | Initial Controls | Initial S | Initial O | Initial D | **Initial RPN** | Recommended Action (Q07 Feature) | Post S | Post O | Post D | **Post RPN** |
|---|---|---|---|---|---|:---:|:---:|:---:|:---:|---|:---:|:---:|:---:|:---:|
| **FM-1** | Product Registration | Malformed SKU Code | Barcode scanner misread; item cannot be tracked; duplicated SKUs | Typo during manual receipt entry | Visual operator check | 7 | 6 | 6 | **252 (High)** | **Feature 1**: Regex mask (`^[A-Z0-9-]{3,20}$`) & SQLite `UNIQUE` constraint | 7 | 1 | 1 | **7 (Low)** |
| **FM-2** | Stock Receipt | Negative Quantity Entry | Corrupts stock valuation; causes false reorder alerts | Operator enters minus sign (`-10`) instead of outward transaction | None in legacy system | 8 | 5 | 5 | **200 (High)** | **Feature 1**: Integer-only parser & SQLite `CHECK (quantity >= 0)` | 8 | 1 | 1 | **8 (Low)** |
| **FM-3** | Category Assignment | Category Inconsistency ("elec", "Electronic") | Distorts category Pareto charts & financial summary | Free-form text input with inconsistent operator spelling | Periodic Excel review | 5 | 7 | 5 | **175 (Med)** | **Feature 2**: Controlled master dropdown selector (`ALLOWED_CATEGORIES`) | 5 | 1 | 1 | **5 (Low)** |
| **FM-4** | Product Deletion | Accidental Catalog Deletion | Permanent data loss; orphaned historical inventory items | Operator accidentally clicks Delete button | None in legacy system | 9 | 3 | 6 | **162 (Med)** | **Feature 4**: Confirmation modal showing item summary & impacts | 9 | 1 | 2 | **18 (Low)** |
| **FM-5** | Stock Adjustment | Unaccounted Stock Variance | Physical and software inventory desynchronized; missing accountability | Variance adjusted without reason or audit trail | Annual manual stock take | 8 | 4 | 4 | **128 (Med)** | **Feature 4 & 5**: Audited adjustment modal requiring reason & JSON diff log | 8 | 1 | 1 | **8 (Low)** |
| **FM-6** | Product Search | Search Query Failure | Operator unable to locate existing item; creates duplicate | Case-sensitive search fails on uppercase/lowercase | None | 4 | 6 | 4 | **96 (Low)** | **Feature 3**: Debounced autocomplete searching name and SKU via indexed `LIKE` | 4 | 1 | 1 | **4 (Low)** |

---

## 3. Results & Risk Reduction Summary

- **Baseline Total RPN**: $252 + 200 + 175 + 162 + 128 + 96 = \mathbf{1,013}$
- **Post-Q07 Total RPN**: $7 + 8 + 5 + 18 + 8 + 4 = \mathbf{50}$
- **Total Risk Reduction**: $\mathbf{95.06\%}$

By replacing manual human vigilance with automated software Poka-Yoke mechanisms (regex validation, controlled dropdowns, confirmation modals, and transactional audit trails), both the **Occurrence ($O$)** and the **Detection ($D$)** factors were minimized to the lowest possible risk rating.
