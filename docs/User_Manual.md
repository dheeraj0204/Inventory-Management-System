# User Manual & Operating Guide

## Desktop Inventory Management System — TQM Q07 Data Accuracy

- **Student**: Dheeraj Khetwal
- **Course**: BBAT104 — Fundamentals of Total Quality Management
- **Academic Session**: 2026–27
- **Target Audience**: Warehouse Clerks, Store Supervisors, Quality Assurance Engineers, University Evaluators

---

## 1. System Requirements & Setup

### 1.1 Prerequisites
- **Operating System**: Windows 10 or Windows 11 (64-bit recommended)
- **Python**: Python 3.11, 3.12, 3.13, or 3.14
- **IDE**: Visual Studio Code (or standard Windows Terminal / PowerShell)
- **Dependencies**: `customtkinter`, `matplotlib`, `pandas`, `pytest`, `pillow`

### 1.2 Installation Instructions (Terminal / VS Code)
Open PowerShell or Visual Studio Code Terminal in the project root directory:

```powershell
# 1. Create a Python virtual environment
py -m venv .venv

# 2. Activate the virtual environment
.\.venv\Scripts\Activate.ps1

# 3. Upgrade pip and install required packages
pip install --upgrade pip
pip install -r requirements.txt
```

### 1.3 Launching the Application
Launch the desktop interface by running:

```powershell
.\.venv\Scripts\python.exe main.py
```

*Note: On initial boot, the application automatically verifies and initializes `data/inventory_tqm.db` with complete schema tables and baseline catalog data.*

---

## 2. Navigating the User Interface

The application features a modern enterprise dark-navy sidebar on the left and a responsive canvas on the right.

### 2.1 Navigation Menu
1. **📊 Dashboard Overview**: High-level inventory statistics, valuation metrics, category distribution chart, and recent audit activity feed.
2. **📦 Product Catalog**: Full CRUD interface for managing inventory products with live autocomplete search and category filters.
3. **⚖️ Inventory & Stock**: Current stock levels, low-stock alerts, audited stock adjustment wizard, and historical movement ledger.
4. **📜 Audit History (Q07)**: Read-only audit log viewer with action filtering and side-by-side JSON diff inspector.
5. **🎯 TQM Quality & Analytics**: Dedicated quality suite containing CTQ scorecard, Pareto 80/20 chart, Fishbone diagram, FMEA matrix, SIPOC map, and PDCA tracker.

---

## 3. Step-by-Step Operator Guide

### 3.1 Adding a New Product (Q07 Poka-Yoke Input Masking)
1. Click **📦 Product Catalog** on the sidebar.
2. Click the blue **+ Add New Product** button in the top right.
3. Fill out the registration form:
   - **Product Name**: Enter 2 to 100 characters (e.g., `Laser Rangefinder`).
   - **Category**: Select from the controlled dropdown (e.g., `Electronics`). Manual typing is blocked to prevent spelling errors.
   - **SKU Code**: Enter uppercase alphanumeric code with hyphens (e.g., `ELEC-RNG-11`). The form automatically normalizes text to uppercase as you type.
   - **Quantity**: Enter whole integer $\ge 0$. Decimals and negative numbers are rejected.
   - **Unit Price**: Enter positive currency amount $> 0.00$.
   - **Reorder Level**: Enter threshold for low-stock warning (defaults to 5).
   - **Supplier Name**: Enter vendor name.
4. Click **Create Product**.
5. *Result*: The system saves the product, logs an `INITIAL` stock movement, and writes a `CREATE` event to the audit log.

### 3.2 Searching Products with Auto-Complete (Q07 Feature 3)
1. In the **Product Catalog**, locate the **Search** box in the toolbar.
2. Type at least 2 characters (e.g., `cal`).
3. An interactive suggestion popover appears below the search box showing real matching database products.
4. Click any suggestion or press Enter to filter the catalog table immediately.
5. Click **Reset Filters** to restore the full catalog view.

### 3.3 Executing an Audited Stock Adjustment (Q07 Feature 4 & 5)
1. Click **⚖️ Inventory & Stock** on the sidebar.
2. Click the amber **⚡ Adjust Stock Level** button.
3. In the modal dialog:
   - Select the target product from the dropdown. The modal automatically displays the current verified stock.
   - Enter the **New Verified Physical Quantity**. As you type, the modal displays a real-time variance calculation ($+N$ or $-N$ units).
   - Select a mandatory **Reason for Stock Adjustment** from the controlled dropdown (e.g., `Stock Count Audit Correction`, `Damaged Goods Write-off`).
4. Click **Apply Adjustment**.
5. A **Confirmation Modal** appears summarizing the product name, previous stock, new stock, variance, and reason.
6. Click **Confirm Adjustment**.
7. *Result*: Stock is transactionally updated, an entry is added to the **Stock Movement Ledger**, and an audit record is stored in `audit_logs`.

### 3.4 Inspecting Audit Event JSON Diffs
1. Click **📜 Audit History (Q07)** on the sidebar.
2. Filter events by Action (`CREATE`, `UPDATE`, `DELETE`, `STOCK_ADJUSTMENT`) or search by Product ID.
3. On any event row, click the blue **Inspect JSON** button.
4. A side-by-side modal opens showing:
   - **Previous Values (Old)**: JSON snapshot before modification (highlighted in red).
   - **Applied Values (New)**: JSON snapshot after modification (highlighted in green).
5. Review the changes and click **Close Inspector**.

### 3.5 Using the TQM Quality Suite
1. Click **🎯 TQM Quality & Analytics** on the sidebar.
2. Explore the 6 tabs:
   - **1. CTQ Scorecard**: Review live compliance percentages for Stock Quantity Integrity, SKU Uniqueness, Data Completeness, Category Standardization, and Audit Coverage.
   - **2. Pareto Analysis**: Review the Matplotlib Pareto chart showing sorted defect categories, cumulative percentage curve, and the green dashed 80% reference line. Use the **+ Log Defect** button to record new observations.
   - **3. Fishbone (Ishikawa)**: Review the 4 course cause categories (People, Process, Software Code, Infrastructure) explaining inventory inaccuracies.
   - **4. FMEA Risk Matrix**: Review potential failure modes and their Risk Priority Numbers ($RPN = S \times O \times D$). Click **+ Add FMEA Item** to evaluate new processes.
   - **5. SIPOC Process Map**: Review the 5-stage inventory flow from Vendors to Customers.
   - **6. PDCA Tracker**: Inspect continuous improvement cycles across Plan, Do, Check, and Act.

---

## 4. Troubleshooting & FAQs

- **Q: What if I enter a negative quantity or letter in price?**
  - *A*: The form immediately displays an inline red error banner explaining the validation rule. The database is never touched.
- **Q: Where is my data saved?**
  - *A*: All data is stored in the local SQLite database at `data/inventory_tqm.db`. It persists across application restarts.
- **Q: How do I run the automated test suite?**
  - *A*: Run `.\.venv\Scripts\pytest tests/ -v` in the terminal. All 42 tests will run against an isolated temporary database.
