"""Generates additional high-resolution visual diagram assets for the presentation."""

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from app.services import tqm_service

out_dir = Path("docs/screenshots")
out_dir.mkdir(parents=True, exist_ok=True)

# -----------------------------------------------------------------------------
# 1. Poka-Yoke CRUD & Modal Workflow Diagram
# -----------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9, 5), dpi=200)
fig.patch.set_facecolor("#0F172A")
ax.set_facecolor("#1E293B")
ax.axis("off")

# Title
ax.text(0.04, 0.92, "POKA-YOKE (MISTAKE PROOFING) & CRUD SAFEGUARDS", fontsize=13, color="#38BDF8", fontweight="bold")
ax.text(0.04, 0.86, "How Quality Goal Q07 prevents invalid data entry at input gates", fontsize=9, color="#94A3B8")

# 3 Columns: [1] Entry Gate, [2] Validation Engine, [3] Persistence & Audit
cols_data = [
    (0.04, 0.28, "1. USER ENTRY TIERS", [
        ("Product Name", "Mandatory, 2-100 characters"),
        ("Category Dropdown", "Controlled 6 master choices"),
        ("SKU Input Mask", "Auto-caps, regex: ^[A-Z0-9-]{3,20}$"),
        ("Quantity Field", "Integer-only, strictly >= 0"),
        ("Unit Price Field", "Positive float, strictly > 0.00"),
    ], "#2563EB"),
    (0.36, 0.28, "2. POKA-YOKE ENGINE", [
        ("Whitespace Normalizer", "Strips & collapses duplicate spaces"),
        ("Pre-Save SKU Lookup", "Detects duplicates before insert"),
        ("Live Error Banner", "Immediate field-specific feedback"),
        ("Confirmation Modals", "Explicit impact summary on delete"),
        ("Variance Calculator", "Live +/- delta on stock adjustment"),
    ], "#D97706"),
    (0.68, 0.28, "3. DATABASE & AUDIT", [
        ("SQLite CHECK Constraints", "quantity >= 0, unit_price > 0"),
        ("UNIQUE Constraints", "product_id UNIQUE, sku UNIQUE"),
        ("Foreign Keys Enforced", "PRAGMA foreign_keys = ON"),
        ("Atomic ACID Rollback", "Zero partial or corrupted writes"),
        ("Immutable JSON Audit", "Before & after values diff logged"),
    ], "#10B981"),
]

for x, w, col_title, items, border_col in cols_data:
    rect = patches.FancyBboxPatch((x, 0.08), w, 0.72, boxstyle="round,pad=0.02,rounding_size=0.03",
                                 facecolor="#1E293B", edgecolor=border_col, linewidth=1.5, transform=ax.transAxes)
    ax.add_patch(rect)
    ax.text(x + 0.02, 0.74, col_title, fontsize=10, color=border_col, fontweight="bold", transform=ax.transAxes)

    for idx, (label, desc) in enumerate(items):
        y = 0.65 - idx * 0.125
        ax.text(x + 0.02, y, f"• {label}", fontsize=8.5, color="#F8FAFC", fontweight="bold", transform=ax.transAxes)
        ax.text(x + 0.04, y - 0.045, desc, fontsize=7.2, color="#94A3B8", transform=ax.transAxes)

plt.tight_layout()
plt.savefig(out_dir / "crud_poka_yoke_flow.png", facecolor=fig.get_facecolor(), edgecolor="none", dpi=200)
plt.close()
print("Generated: docs/screenshots/crud_poka_yoke_flow.png")

# -----------------------------------------------------------------------------
# 2. Ishikawa (Fishbone) 4M Root Cause Diagram
# -----------------------------------------------------------------------------
fig2, ax2 = plt.subplots(figsize=(9.5, 5), dpi=200)
fig2.patch.set_facecolor("#0F172A")
ax2.set_facecolor("#1E293B")
ax2.axis("off")

# Title
ax2.text(0.04, 0.93, "ISHIKAWA CAUSE-AND-EFFECT (FISHBONE) DIAGRAM", fontsize=13, color="#38BDF8", fontweight="bold")
ax2.text(0.04, 0.87, "4M Course Context Analysis for Inventory Data Inaccuracies (Q07)", fontsize=9, color="#94A3B8")

# Central Spine
ax2.annotate("", xy=(0.88, 0.48), xytext=(0.04, 0.48),
             arrowprops=dict(arrowstyle="->", color="#38BDF8", lw=3.0))

# Head (Effect)
head_box = patches.FancyBboxPatch((0.82, 0.36), 0.16, 0.24, boxstyle="round,pad=0.02",
                                 facecolor="#DC2626", edgecolor="#FCA5A5", linewidth=1.8, transform=ax2.transAxes)
ax2.add_patch(head_box)
ax2.text(0.90, 0.48, "INVENTORY\nDATA\nINACCURACY", fontsize=8.5, color="#FFFFFF", fontweight="bold", ha="center", va="center", transform=ax2.transAxes)

# 4 Bones: People, Process (Top); Software Code, Infrastructure (Bottom)
bones = [
    # Top Left: PEOPLE
    ("PEOPLE", (0.24, 0.48), (0.16, 0.78), [
        "Clerk fatigue during rapid entry",
        "Typo in unit price & decimal omission",
        "Lack of standardized SKU training",
    ], "#38BDF8", "top"),
    # Top Right: PROCESS
    ("PROCESS", (0.60, 0.48), (0.52, 0.78), [
        "Unconfirmed stock write-offs",
        "Delayed physical stock reconciliation",
        "No written standard for categories",
    ], "#FBBF24", "top"),
    # Bottom Left: SOFTWARE CODE
    ("SOFTWARE CODE", (0.24, 0.48), (0.16, 0.18), [
        "Missing regex input masking in legacy UI",
        "Lack of atomic transaction rollback",
        "Negative quantity accepted into DB",
    ], "#F43F5E", "bottom"),
    # Bottom Right: INFRASTRUCTURE
    ("INFRASTRUCTURE", (0.60, 0.48), (0.52, 0.18), [
        "Barcode scanner smudge misreads",
        "Unreliable file locks during writes",
        "Lack of automated schema migrations",
    ], "#34D399", "bottom"),
]

for cat_name, spine_pt, bone_end, causes, col, side in bones:
    # Bone line
    ax2.plot([spine_pt[0], bone_end[0]], [spine_pt[1], bone_end[1]], color=col, lw=2.0)
    # Category Label Box
    c_box = patches.FancyBboxPatch((bone_end[0] - 0.08, bone_end[1] - 0.035 if side=="top" else bone_end[1] - 0.01),
                                  0.16, 0.06, boxstyle="round,pad=0.01",
                                  facecolor=col, edgecolor="none", transform=ax2.transAxes)
    ax2.add_patch(c_box)
    ax2.text(bone_end[0], bone_end[1] - 0.005 if side=="top" else bone_end[1] + 0.02,
             cat_name, fontsize=8, color="#0F172A", fontweight="bold", ha="center", transform=ax2.transAxes)

    # Sub-causes
    for i, cause in enumerate(causes):
        y_c = (bone_end[1] - 0.07 - i * 0.05) if side == "top" else (bone_end[1] + 0.08 + i * 0.05)
        x_c = bone_end[0] + 0.02
        ax2.text(x_c, y_c, f"- {cause}", fontsize=7.2, color="#E2E8F0", transform=ax2.transAxes)

plt.tight_layout()
plt.savefig(out_dir / "fishbone_diagram.png", facecolor=fig2.get_facecolor(), edgecolor="none", dpi=200)
plt.close()
print("Generated: docs/screenshots/fishbone_diagram.png")

# -----------------------------------------------------------------------------
# 3. SIPOC Process Flow Diagram
# -----------------------------------------------------------------------------
fig3, ax3 = plt.subplots(figsize=(9.5, 4.2), dpi=200)
fig3.patch.set_facecolor("#0F172A")
ax3.set_facecolor("#1E293B")
ax3.axis("off")

ax3.text(0.04, 0.90, "SIPOC PROCESS FLOW MAP — INVENTORY LIFECYCLE (Q07)", fontsize=13, color="#38BDF8", fontweight="bold")
ax3.text(0.04, 0.83, "Suppliers -> Inputs -> Process Steps -> Outputs -> Customers", fontsize=9, color="#94A3B8")

sipoc_cols = [
    ("SUPPLIERS", 0.04, "#3B82F6", ["Vendors", "Receiving Clerks", "Storekeepers", "System Database"]),
    ("INPUTS", 0.23, "#0284C7", ["Delivery Challan", "Physical Goods", "Master SKU Codes", "Reorder Thresholds"]),
    ("PROCESS", 0.42, "#D97706", ["1. Inward Verification", "2. Poka-Yoke Registration", "3. Storage Allocation", "4. Audited Adjustment"]),
    ("OUTPUTS", 0.61, "#10B981", ["Validated Catalog", "Real-Time Stock Ledger", "Stock Movement Row", "JSON Audit Trail"]),
    ("CUSTOMERS", 0.80, "#8B5CF6", ["Production Lines", "Store Supervisors", "Quality Auditors", "Finance Controllers"]),
]

for title, x, col, items in sipoc_cols:
    box = patches.FancyBboxPatch((x, 0.08), 0.16, 0.68, boxstyle="round,pad=0.02",
                                facecolor="#1E293B", edgecolor=col, linewidth=1.5, transform=ax3.transAxes)
    ax3.add_patch(box)
    t_box = patches.FancyBboxPatch((x, 0.68), 0.16, 0.08, boxstyle="round,pad=0.01",
                                  facecolor=col, edgecolor="none", transform=ax3.transAxes)
    ax3.add_patch(t_box)
    ax3.text(x + 0.08, 0.72, title, fontsize=8.5, color="#FFFFFF", fontweight="bold", ha="center", transform=ax3.transAxes)

    for idx, it in enumerate(items):
        y = 0.58 - idx * 0.12
        ax3.text(x + 0.015, y, f"• {it}", fontsize=7.5, color="#E2E8F0", transform=ax3.transAxes)

plt.tight_layout()
plt.savefig(out_dir / "sipoc_workflow.png", facecolor=fig3.get_facecolor(), edgecolor="none", dpi=200)
plt.close()
print("Generated: docs/screenshots/sipoc_workflow.png")
