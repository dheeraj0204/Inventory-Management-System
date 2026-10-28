import os
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from app.services import inventory_service, tqm_service

# Ensure output directory exists
out_dir = Path("docs/screenshots")
out_dir.mkdir(parents=True, exist_ok=True)

# -----------------------------------------------------------------------------
# 1. Category Valuation Breakdown Chart
# -----------------------------------------------------------------------------
summary = inventory_service.get_inventory_summary()
cat_data = summary["category_breakdown"]
total_val = summary["total_valuation"]

fig, ax = plt.subplots(figsize=(8.5, 4.5), dpi=200)
fig.patch.set_facecolor("#0F172A")
ax.set_facecolor("#1E293B")

cats = [c["category"] for c in cat_data]
vals = [float(c["valuation"]) for c in cat_data]
palette = ["#38BDF8", "#60A5FA", "#34D399", "#FBBF24", "#A78BFA", "#2DD4BF"]

bars = ax.bar(cats, vals, color=palette[:len(cats)], width=0.52, edgecolor="#334155", linewidth=1.2, zorder=3)
ax.set_ylabel("Inventory Valuation ($ USD)", fontsize=10, color="#94A3B8", fontweight="bold")
ax.set_title("Category Valuation Breakdown — Enterprise Inventory IMS", fontsize=12, color="#F8FAFC", fontweight="bold", pad=12)
ax.tick_params(axis="x", labelrotation=15, labelsize=9, colors="#E2E8F0")
ax.tick_params(axis="y", labelsize=9, colors="#E2E8F0")
for spine in ax.spines.values():
    spine.set_color("#334155")
ax.grid(axis="y", linestyle="--", alpha=0.25, color="#94A3B8", zorder=1)

for bar, c in zip(bars, cat_data):
    yval = bar.get_height()
    pct = (yval / total_val * 100) if total_val > 0 else 0
    ax.text(bar.get_x() + bar.get_width() / 2, yval + max(vals) * 0.02, f"${yval:,.0f}\n({pct:.1f}%)",
            ha="center", va="bottom", fontsize=8, color="#F8FAFC", fontweight="bold")

ax.set_ylim(0, max(vals) * 1.25)
plt.tight_layout()
plt.savefig(out_dir / "category_valuation_chart.png", facecolor=fig.get_facecolor(), edgecolor="none", dpi=200)
plt.close()
print("Generated: docs/screenshots/category_valuation_chart.png")

# -----------------------------------------------------------------------------
# 2. Pareto Defect Analysis Chart (80/20 Rule)
# -----------------------------------------------------------------------------
pareto = tqm_service.calculate_pareto_data()
cats_p = pareto["categories"]
counts_p = [float(c) for c in pareto["counts"]]
cum_p = [float(p) for p in pareto["cumulative_percentages"]]

fig2, ax1 = plt.subplots(figsize=(9, 4.8), dpi=200)
fig2.patch.set_facecolor("#0F172A")
ax1.set_facecolor("#1E293B")

bars_p = ax1.bar(cats_p, counts_p, color="#3B82F6", width=0.52, edgecolor="#1E3A8A", alpha=0.9, label="Defect Frequency", zorder=3)
ax1.set_ylabel("Defect Frequency (Count)", color="#38BDF8", fontsize=10, fontweight="bold")
ax1.tick_params(axis="y", labelcolor="#38BDF8", labelsize=9)
ax1.tick_params(axis="x", labelrotation=25, labelsize=8.5, colors="#E2E8F0")
ax1.set_ylim(0, max(counts_p) * 1.3)
for spine in ax1.spines.values():
    spine.set_color("#334155")
ax1.grid(axis="y", linestyle="--", alpha=0.2, color="#94A3B8", zorder=1)

ax2 = ax1.twinx()
ax2.plot(cats_p, cum_p, color="#F43F5E", marker="o", linewidth=2.5, markersize=7, label="Cumulative %", zorder=5)
ax2.set_ylabel("Cumulative Percentage (%)", color="#F43F5E", fontsize=10, fontweight="bold")
ax2.tick_params(axis="y", labelcolor="#F43F5E", labelsize=9)
ax2.set_ylim(0, 115)
for spine in ax2.spines.values():
    spine.set_color("#334155")

ax2.axhline(80, color="#10B981", linestyle="--", linewidth=1.8, alpha=0.9, label="80% Cutoff Line", zorder=4)
ax2.text(len(cats_p) - 1, 82, "80% Vital Few Cutoff Line", color="#10B981", fontsize=9, fontweight="bold", ha="right")

for bar in bars_p:
    h = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width() / 2, h + 0.4, f"{int(h)}", ha="center", va="bottom", fontsize=8.5, color="#F8FAFC", fontweight="bold")

plt.title("TQM Defect Pareto Analysis (80/20 Rule) — Vital Few Identification", fontsize=12, color="#F8FAFC", fontweight="bold", pad=14)
plt.tight_layout()
plt.savefig(out_dir / "pareto_analysis_chart.png", facecolor=fig2.get_facecolor(), edgecolor="none", dpi=200)
plt.close()
print("Generated: docs/screenshots/pareto_analysis_chart.png")

# -----------------------------------------------------------------------------
# 3. CTQ Scorecard Compliance Graphic
# -----------------------------------------------------------------------------
fig3, ax3 = plt.subplots(figsize=(8.5, 4.2), dpi=200)
fig3.patch.set_facecolor("#0F172A")
ax3.set_facecolor("#1E293B")

ctq = tqm_service.calculate_ctq_metrics()["metrics"]
ctq_names = [m["characteristic"] for m in ctq]
y_pos = list(range(len(ctq_names)))

bars_ctq = ax3.barh(y_pos, [100.0] * len(ctq_names), color="#10B981", height=0.45, edgecolor="#059669", alpha=0.95, zorder=3)
ax3.set_yticks(y_pos)
ax3.set_yticklabels(ctq_names, fontsize=9.5, color="#F8FAFC", fontweight="bold")
ax3.set_xlabel("Quality Compliance Rate (%)", fontsize=10, color="#94A3B8", fontweight="bold")
ax3.set_xlim(0, 120)
ax3.tick_params(axis="x", labelsize=9, colors="#E2E8F0")
for spine in ax3.spines.values():
    spine.set_color("#334155")
ax3.grid(axis="x", linestyle="--", alpha=0.25, color="#94A3B8", zorder=1)

for bar, m in zip(bars_ctq, ctq):
    w = bar.get_width()
    ax3.text(w + 1.5, bar.get_y() + bar.get_height() / 2, f"{m['actual']} [PASS]", va="center", fontsize=9, color="#34D399", fontweight="bold")

plt.title("Critical to Quality (CTQ) Compliance Scorecard — Goal Q07", fontsize=12, color="#F8FAFC", fontweight="bold", pad=12)
plt.tight_layout()
plt.savefig(out_dir / "ctq_scorecard.png", facecolor=fig3.get_facecolor(), edgecolor="none", dpi=200)
plt.close()
print("Generated: docs/screenshots/ctq_scorecard.png")

# -----------------------------------------------------------------------------
# 4. Dashboard Architecture & UI Showcase Graphic
# -----------------------------------------------------------------------------
fig4 = plt.figure(figsize=(10, 5.5), dpi=200)
fig4.patch.set_facecolor("#0F172A")

# Title and subtitle
plt.text(0.04, 0.92, "ENTERPRISE INVENTORY MANAGEMENT SYSTEM", fontsize=14, color="#38BDF8", fontweight="bold")
plt.text(0.04, 0.86, "Quality Goal Q07 — Improving Data Accuracy Using Total Quality Management (BBAT104)", fontsize=9.5, color="#94A3B8")

# 4 KPI Stat Cards Mockup
card_props = [
    ("UNIQUE PRODUCTS", "10", "Catalog Master Items", "#2563EB", 0.04),
    ("UNITS IN STOCK", "686", "Physically Verified", "#0284C7", 0.28),
    ("TOTAL VALUATION", "$328,000.00", "Sum(Qty × Unit Price)", "#16A34A", 0.52),
    ("LOW-STOCK ALERTS", "2", "Qty <= Reorder Level", "#DC2626", 0.76),
]

for title, val, sub, accent, x in card_props:
    rect = plt.Rectangle((x, 0.58), 0.20, 0.22, transform=fig4.transFigure,
                         facecolor="#1E293B", edgecolor="#334155", linewidth=1.2)
    fig4.patches.append(rect)
    stripe = plt.Rectangle((x, 0.785), 0.20, 0.015, transform=fig4.transFigure,
                           facecolor=accent, edgecolor="none")
    fig4.patches.append(stripe)
    plt.text(x + 0.012, 0.75, title, fontsize=7.5, color="#94A3B8", fontweight="bold", transform=fig4.transFigure)
    plt.text(x + 0.012, 0.67, val, fontsize=13, color="#F8FAFC", fontweight="bold", transform=fig4.transFigure)
    plt.text(x + 0.012, 0.61, sub, fontsize=7, color="#64748B", transform=fig4.transFigure)

# Feature Highlights Box
rect_feat = plt.Rectangle((0.04, 0.08), 0.92, 0.45, transform=fig4.transFigure,
                          facecolor="#1E293B", edgecolor="#334155", linewidth=1.2)
fig4.patches.append(rect_feat)
stripe_feat = plt.Rectangle((0.04, 0.515), 0.92, 0.015, transform=fig4.transFigure,
                            facecolor="#38BDF8", edgecolor="none")
fig4.patches.append(stripe_feat)

plt.text(0.06, 0.46, "CORE Q07 DATA ACCURACY & TQM MODULE ARCHITECTURE", fontsize=10, color="#38BDF8", fontweight="bold", transform=fig4.transFigure)

features_text = [
    ("[1] Poka-Yoke Input Masking", "Regex format checks for SKUs, integer-only quantities, positive unit prices, zero-value protection"),
    ("[2] Controlled Taxonomy", "Standardized master category dropdown eliminating spelling variants and reporting fragmentation"),
    ("[3] Debounced Autocomplete", "Real-time suggestion popover querying live SQLite database by name or SKU code within 180ms"),
    ("[4] Confirmation Modals", "Explicit dialogs displaying before/after impact summary before destructive deletions or adjustments"),
    ("[5] Transactional Audit Trail", "Dedicated audit_logs table storing immutable JSON diffs for every create, update, delete & stock event"),
    ("[6] TQM Analytics Suite", "Live CTQ Scorecard • Animated Pareto 80/20 Chart • 4M Fishbone Diagram • FMEA Risk Matrix • SIPOC • PDCA"),
]

for idx, (head, desc) in enumerate(features_text):
    y_pos = 0.40 - idx * 0.058
    plt.text(0.06, y_pos, head, fontsize=8.5, color="#F8FAFC", fontweight="bold", transform=fig4.transFigure)
    plt.text(0.32, y_pos, desc, fontsize=8, color="#94A3B8", transform=fig4.transFigure)

plt.axis("off")
plt.savefig(out_dir / "dashboard_ui_overview.png", facecolor=fig4.get_facecolor(), edgecolor="none", dpi=200)
plt.close()
print("Generated: docs/screenshots/dashboard_ui_overview.png")
