"""Builds the comprehensive Review 1 & 2 PowerPoint presentation for BBAT104 TQM."""

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# Initialize Presentation with 16:9 widescreen
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

# Theme Colors
BG_DARK = RGBColor(15, 23, 42)       # Slate 900
CARD_BG = RGBColor(30, 41, 59)       # Slate 800
CARD_BORDER = RGBColor(51, 65, 85)   # Slate 700
ACCENT_BLUE = RGBColor(56, 189, 248) # Sky 400
PRIMARY = RGBColor(37, 99, 235)      # Blue 600
SUCCESS = RGBColor(16, 185, 129)     # Emerald 500
WARNING = RGBColor(245, 158, 11)     # Amber 500
DANGER = RGBColor(239, 68, 68)       # Red 500
TEXT_WHITE = RGBColor(248, 250, 252) # Slate 50
TEXT_MUTED = RGBColor(148, 163, 184) # Slate 400

screenshots_dir = Path("docs/screenshots")


def add_base_slide(title_text: str, subtitle_text: str = "", review_badge: str = "BBAT104 TQM"):
    """Helper to create a consistent dark enterprise themed slide with header."""
    slide = prs.slides.add_slide(blank_layout)

    # Full Background
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = BG_DARK
    bg.line.fill.background()

    # Top Accent Line
    top_line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(0.08))
    top_line.fill.solid()
    top_line.fill.fore_color.rgb = ACCENT_BLUE
    top_line.line.fill.background()

    # Review Badge
    if review_badge:
        badge_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.35), Inches(4.0), Inches(0.35))
        tf_b = badge_box.text_frame
        tf_b.word_wrap = True
        p_b = tf_b.paragraphs[0]
        p_b.text = review_badge.upper()
        p_b.font.size = Pt(10)
        p_b.font.bold = True
        p_b.font.color.rgb = ACCENT_BLUE

    # Title
    t_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.65), Inches(11.5), Inches(0.6))
    tf = t_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title_text
    p.font.size = Pt(22)
    p.font.bold = True
    p.font.color.rgb = TEXT_WHITE

    # Subtitle
    if subtitle_text:
        s_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.25), Inches(11.5), Inches(0.4))
        tf_s = s_box.text_frame
        p_s = tf_s.paragraphs[0]
        p_s.text = subtitle_text
        p_s.font.size = Pt(11)
        p_s.font.color.rgb = TEXT_MUTED

    # Bottom Footer
    f_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.0), Inches(11.7), Inches(0.3))
    tf_f = f_box.text_frame
    p_f = tf_f.paragraphs[0]
    p_f.text = "Student: Dheeraj Khetwal | Course: BBAT104 — Fundamentals of TQM | Quality Goal: Q07 — Improve Data Accuracy"
    p_f.font.size = Pt(9)
    p_f.font.color.rgb = TEXT_MUTED

    return slide


def add_card(slide, left, top, width, height, title="", border_color=CARD_BORDER):
    """Helper to draw a styled card container."""
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = CARD_BG
    card.line.color.rgb = border_color
    card.line.width = Pt(1.5)

    if title:
        t_box = slide.shapes.add_textbox(left + Inches(0.15), top + Inches(0.12), width - Inches(0.3), Inches(0.4))
        tf = t_box.text_frame
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = ACCENT_BLUE

    return card


# =============================================================================
# SLIDE 1: Title Slide (Hero Academic Identity)
# =============================================================================
slide1 = prs.slides.add_slide(blank_layout)
bg1 = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
bg1.fill.solid()
bg1.fill.fore_color.rgb = BG_DARK
bg1.line.fill.background()

# Hero Header Bar
stripe1 = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.0), Inches(11.7), Inches(0.1))
stripe1.fill.solid()
stripe1.fill.fore_color.rgb = ACCENT_BLUE
stripe1.line.fill.background()

t_box1 = slide1.shapes.add_textbox(Inches(0.8), Inches(1.3), Inches(11.7), Inches(2.2))
tf1 = t_box1.text_frame
p1 = tf1.paragraphs[0]
p1.text = "Inventory Management System"
p1.font.size = Pt(36)
p1.font.bold = True
p1.font.color.rgb = TEXT_WHITE

p1_sub = tf1.add_paragraph()
p1_sub.text = "Improving Data Accuracy Using Total Quality Management (Q07)"
p1_sub.font.size = Pt(20)
p1_sub.font.bold = True
p1_sub.font.color.rgb = ACCENT_BLUE

p1_tag = tf1.add_paragraph()
p1_tag.text = "SRS Review 1 & Review 2 Presentation: Process, Architecture, Poka-Yoke & TQM Analytics"
p1_tag.font.size = Pt(13)
p1_tag.font.color.rgb = TEXT_MUTED

# Metadata Grid Cards
card_info = [
    ("STUDENT NAME", "Dheeraj Khetwal", "Lead Developer & TQM Analyst", Inches(0.8)),
    ("COURSE", "BBAT104", "Fundamentals of TQM", Inches(3.85)),
    ("ACADEMIC SESSION", "2026–27", "Undergraduate Project", Inches(6.90)),
    ("ASSIGNED GOAL", "Goal Q07", "Improve Data Accuracy", Inches(9.95)),
]

for title, val, sub, left in card_info:
    add_card(slide1, left, Inches(3.8), Inches(2.6), Inches(2.5), title=title, border_color=PRIMARY)
    c_box = slide1.shapes.add_textbox(left + Inches(0.15), Inches(4.5), Inches(2.3), Inches(1.5))
    tf = c_box.text_frame
    p = tf.paragraphs[0]
    p.text = val
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = TEXT_WHITE
    p_sub = tf.add_paragraph()
    p_sub.text = sub
    p_sub.font.size = Pt(11)
    p_sub.font.color.rgb = TEXT_MUTED

# =============================================================================
# SLIDE 2: Review 1 — Vision, Mission & Quality Objective
# =============================================================================
slide2 = add_base_slide("Vision, Mission & Quality Objective",
                        "Setting the foundational quality philosophy for the software lifecycle",
                        "Review 1 — Setup & SRS")

cards2 = [
    ("VISION", "A zero-defect warehouse inventory ecosystem where no incorrect, duplicate, or unverified stock entry ever enters the database.", SUCCESS, Inches(0.8)),
    ("MISSION", "Build a production-grade desktop application that validates inputs at the gate (Poka-Yoke), locks processes, and preserves immutable audit logs.", PRIMARY, Inches(4.8)),
    ("QUALITY OBJECTIVE (Q07)", "1. Error prevention at source (Input Masking)\n2. Process control (Controlled Categories & Transactions)\n3. Monitoring & Traceability (Audit Logs & TQM Charts)", WARNING, Inches(8.8)),
]

for title, text, col, left in cards2:
    add_card(slide2, left, Inches(1.8), Inches(3.7), Inches(4.8), title=title, border_color=col)
    t_box = slide2.shapes.add_textbox(left + Inches(0.2), Inches(2.5), Inches(3.3), Inches(3.8))
    tf = t_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(14)
    p.font.color.rgb = TEXT_WHITE

# =============================================================================
# SLIDE 3: Review 1 — Baseline Understanding & Problem Statement
# =============================================================================
slide3 = add_base_slide("Baseline Understanding & Problem Statement",
                        "Quantifying the Cost of Poor Quality (COPQ) in traditional inventory systems",
                        "Review 1 — Setup & SRS")

add_card(slide3, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8), title="BASELINE PROBLEMS IN LEGACY SYSTEMS", border_color=DANGER)
t_box3a = slide3.shapes.add_textbox(Inches(1.0), Inches(2.4), Inches(5.2), Inches(4.0))
tf3a = t_box3a.text_frame
tf3a.word_wrap = True
problems = [
    "Negative & Decimal Quantities: Operators enter '-10' or '12.5', corrupting inventory ledgers.",
    "Unchecked Monetary Fields: Strings or zero-prices entered during rapid invoice receiving.",
    "Fragmented Categories: Free text allows 'elec', 'Electronic', 'ELECT' to split reporting.",
    "Duplicate Identifiers: Accidental duplicate SKUs cause barcode scan failures and orphaned stock.",
    "Untracked Stock Variances: Manual stock write-offs without supervisor sign-off or recorded reasons.",
    "Accidental Deletions: One click permanently wipes historical catalog records.",
]
for p_text in problems:
    p = tf3a.add_paragraph()
    p.text = "• " + p_text
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_WHITE
    p.space_after = Pt(8)

add_card(slide3, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.8), title="TQM QUALITY GOAL Q07 SOLUTION", border_color=SUCCESS)
t_box3b = slide3.shapes.add_textbox(Inches(7.0), Inches(2.4), Inches(5.3), Inches(4.0))
tf3b = t_box3b.text_frame
tf3b.word_wrap = True
solutions = [
    "Poka-Yoke Input Gates: ProductValidator rejects malformed entries before reaching SQLite.",
    "Controlled Taxonomies: 6 standard master categories in OptionMenu; manual typing blocked.",
    "Automated Barcode Masking: Uppercase SKU regex enforcement (^[A-Z0-9-]{3,20}$).",
    "Confirmation Modals: Explicit impact summary before any delete or stock adjustment.",
    "Transactional Audit Trail: Immutable audit_logs table storing JSON diffs of old & new values.",
    "Deming PDCA Loop: Measured defect data continuously feeds Pareto, FMEA, and CTQ scorecards.",
]
for s_text in solutions:
    p = tf3b.add_paragraph()
    p.text = "✓ " + s_text
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_WHITE
    p.space_after = Pt(8)

# =============================================================================
# SLIDE 4: Review 1 — Three Core Quality Ideas Behind the Software
# =============================================================================
slide4 = add_base_slide("Three Quality Ideas Behind the Software",
                        "The TQM engineering pillars powering the entire software design",
                        "Review 1 — Setup & SRS")

ideas = [
    ("1. ERROR PREVENTION AT SOURCE", "POKA-YOKE", [
        "Blank names blocked",
        "Negative quantity blocked",
        "Duplicate SKU blocked",
        "Decimal in quantity blocked",
        "Non-positive price blocked",
    ], PRIMARY, Inches(0.8)),
    ("2. PROCESS CONTROL", "STANDARDIZATION", [
        "One path for all work",
        "Controlled category dropdown",
        "Mandatory adjustment reasons",
        "Atomic ACID transactions",
        "UI cannot bypass validation",
    ], WARNING, Inches(4.8)),
    ("3. MONITORING & TRACEABILITY", "SEE AND TRACE", [
        "Real-time Dashboard alerts",
        "Immutable JSON audit logs",
        "Defect checksheets",
        "Pareto 80/20 root cause chart",
        "Live CTQ scorecard",
    ], SUCCESS, Inches(8.8)),
]

for title, sub, bullets, col, left in ideas:
    add_card(slide4, left, Inches(1.8), Inches(3.7), Inches(4.8), title=title, border_color=col)
    t_box = slide4.shapes.add_textbox(left + Inches(0.2), Inches(2.4), Inches(3.3), Inches(4.0))
    tf = t_box.text_frame
    p_sub = tf.paragraphs[0]
    p_sub.text = f"TQM Pillar: {sub}"
    p_sub.font.size = Pt(11)
    p_sub.font.bold = True
    p_sub.font.color.rgb = col
    p_sub.space_after = Pt(12)

    for b in bullets:
        p = tf.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_WHITE
        p.space_after = Pt(8)

# =============================================================================
# SLIDE 5: Review 1 — Scope and User Roles
# =============================================================================
slide5 = add_base_slide("System Scope & Stakeholder Roles",
                        "Clear separation of user responsibilities aligned with quality governance",
                        "Review 1 — Setup & SRS")

roles = [
    ("WAREHOUSE RECEIVING CLERK", [
        "Primary Task: Register new goods inward",
        "Input: Supplier note, item name, SKU, price",
        "Guards: Poka-Yoke regex & dropdown selection",
        "Cannot do: Delete catalog items, bypass validation",
    ], Inches(0.8), PRIMARY),
    ("STORE SUPERVISOR", [
        "Primary Task: Stock allocations & cycle counts",
        "Action: Audited Stock Level Adjustment",
        "Guards: Mandatory reason selection & confirmation modal",
        "Result: Generates movement transaction & audit log",
    ], Inches(4.8), WARNING),
    ("QUALITY AUDITOR & TQM LEAD", [
        "Primary Task: Verify data integrity & analytics",
        "Tools: CTQ Scorecard, Pareto 80/20, FMEA, PDCA",
        "Access: Read-only inspection of JSON audit logs",
        "Outcome: Drive continuous improvement cycles",
    ], Inches(8.8), SUCCESS),
]

for title, pts, left, col in roles:
    add_card(slide5, left, Inches(1.8), Inches(3.7), Inches(4.8), title=title, border_color=col)
    t_box = slide5.shapes.add_textbox(left + Inches(0.2), Inches(2.5), Inches(3.3), Inches(3.8))
    tf = t_box.text_frame
    for idx, pt in enumerate(pts):
        p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
        p.text = pt
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_WHITE
        p.space_after = Pt(10)

# =============================================================================
# SLIDE 6: Review 1 — Measurable Requirements (Viva Numbers You Can Count)
# =============================================================================
slide6 = add_base_slide("Measurable Requirements (Viva Metrics)",
                        "Translating qualitative stakeholder needs into empirical numbers we can count",
                        "Review 1 — Setup & SRS")

table_shape = slide6.shapes.add_table(7, 4, Inches(0.8), Inches(1.8), Inches(11.7), Inches(4.8))
tbl = table_shape.table
tbl.columns[0].width = Inches(2.6)
tbl.columns[1].width = Inches(3.5)
tbl.columns[2].width = Inches(2.6)
tbl.columns[3].width = Inches(3.0)

headers = ["Quality Need", "Measurable Requirement", "Target Metric", "How It Is Enforced"]
for i, h in enumerate(headers):
    cell = tbl.cell(0, i)
    cell.fill.solid()
    cell.fill.fore_color.rgb = PRIMARY
    p = cell.text_frame.paragraphs[0]
    p.text = h
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = TEXT_WHITE

rows_data = [
    ("No Negative Stock", "Negative quantity entry attempts blocked", "100% Rejection", "ProductValidator + SQLite CHECK (qty >= 0)"),
    ("No Duplicate SKUs", "Number of duplicate SKU registrations", "Exactly 0 duplicates", "Pre-save query + SQLite UNIQUE constraint"),
    ("Clean Taxonomy", "Compliance to 6 master category choices", "100% Compliance", "Controlled CTkOptionMenu dropdown list"),
    ("Trace Every Change", "Catalog edits & adjustments audited", "100% Audit Coverage", "Atomic transaction writes to audit_logs"),
    ("Fast Product Find", "Debounced auto-complete suggestion delay", "< 200 milliseconds", "180ms debounce + indexed SQLite query"),
    ("Prevent Accidental Loss", "Unconfirmed deletion & adjustment events", "0 Unconfirmed Events", "CustomTkinter ConfirmDialog modal window"),
]

for row_idx, r_data in enumerate(rows_data, start=1):
    for col_idx, text in enumerate(r_data):
        cell = tbl.cell(row_idx, col_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = CARD_BG if row_idx % 2 == 0 else RGBColor(24, 34, 53)
        p = cell.text_frame.paragraphs[0]
        p.text = text
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_WHITE if col_idx != 2 else SUCCESS
        if col_idx == 2:
            p.font.bold = True

# =============================================================================
# SLIDE 7: Review 1 — Measurable Quality Objectives (O1 to O5)
# =============================================================================
slide7 = add_base_slide("Measurable Quality Objectives (O1 to O5)",
                        "Formal quality objectives mandated for Course BBAT104 project acceptance",
                        "Review 1 — Setup & SRS")

objs = [
    ("O1: ZERO INVALID DATABASE ENTRIES", "100% of invalid inputs (empty name, negative stock, decimal qty, non-positive price, bad SKU) are rejected before persistence.", PRIMARY, Inches(0.8), Inches(1.8)),
    ("O2: 100% RELATIONAL INTEGRITY", "Zero duplicate SKUs or product IDs. Foreign keys enforced across products, stock_movements, and audit_logs.", SUCCESS, Inches(6.8), Inches(1.8)),
    ("O3: 100% AUDIT TRAIL COVERAGE", "Every product creation, update, deletion, and stock adjustment generates an immutable JSON diff snapshot.", WARNING, Inches(0.8), Inches(4.3)),
    ("O4: TRANSACTIONAL ATOMICITY", "Multi-table modifications save completely or roll back entirely. Zero partial writes or broken audit records.", DANGER, Inches(6.8), Inches(4.3)),
]

for title, desc, col, left, top in objs:
    add_card(slide7, left, top, Inches(5.7), Inches(2.2), title=title, border_color=col)
    t_box = slide7.shapes.add_textbox(left + Inches(0.2), top + Inches(0.6), Inches(5.3), Inches(1.4))
    tf = t_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = desc
    p.font.size = Pt(12)
    p.font.color.rgb = TEXT_WHITE

# =============================================================================
# SLIDE 8: Review 1 — Assigned Quality Goal Q07 (5 Mandatory Features)
# =============================================================================
slide8 = add_base_slide("Assigned Quality Goal Q07 — 5 Mandatory Features",
                        "Core features mandated by the university for Quality Goal Q07 (Improve Data Accuracy)",
                        "Review 1 — Setup & SRS")

q07_features = [
    ("FEATURE 1: INPUT MASKING & STRICT VALIDATION", "Poka-Yoke regex mask for SKU (^[A-Z0-9-]{3,20}$), integer-only quantities, positive unit price (> 0.00), whitespace normalizer.", Inches(1.8), PRIMARY),
    ("FEATURE 2: CONTROLLED DROPDOWN LISTS", "Eliminates category spelling fragmentation. Restricts options to 6 standardized master categories in CustomTkinter OptionMenu.", Inches(2.8), SUCCESS),
    ("FEATURE 3: SEARCH WITH AUTO-COMPLETE", "180ms debounced search suggestion popover querying real database records by name or SKU to prevent duplicate catalog entries.", Inches(3.8), ACCENT_BLUE),
    ("FEATURE 4: CONFIRMATION MODALS", "CustomTkinter modal dialog displaying before/after impact summary before destructive deletions or sensitive stock adjustments.", Inches(4.8), WARNING),
    ("FEATURE 5: TRANSACTIONAL AUDIT LOGGING", "Dedicated audit_logs table storing JSON diffs of previous vs new values. Dedicated history screen with side-by-side JSON diff inspector.", Inches(5.8), DANGER),
]

for title, desc, top, col in q07_features:
    add_card(slide8, Inches(0.8), top, Inches(11.7), Inches(0.85), title=title, border_color=col)
    t_box = slide8.shapes.add_textbox(Inches(1.0), top + Inches(0.4), Inches(11.3), Inches(0.4))
    tf = t_box.text_frame
    p = tf.paragraphs[0]
    p.text = desc
    p.font.size = Pt(10.5)
    p.font.color.rgb = TEXT_WHITE

# =============================================================================
# SLIDE 9: Review 1 — Crucial Viva Mapping (Say This in Viva)
# =============================================================================
slide9 = add_base_slide("Crucial Viva Mapping (The Golden Formula)",
                        "How every software feature directly maps to a TQM principle and customer need",
                        "Review 1 — Setup & SRS")

viva_steps = [
    ("1. CUSTOMER NEED", "Accurate, trustworthy inventory records that reflect physical warehouse reality.", Inches(0.8), PRIMARY),
    ("2. MEASURABLE REQUIREMENT", "Negative quantity attempts = 0, Duplicate SKUs = 0, Category compliance = 100%.", Inches(3.2), SUCCESS),
    ("3. PROCESS CONTROL", "Validation gatekeeper blocks invalid forms; UI cannot bypass service rules.", Inches(5.6), WARNING),
    ("4. AUDIT & MONITORING", "JSON audit logs, real-time dashboard alerts, defect checksheets & Pareto 80/20.", Inches(8.0), ACCENT_BLUE),
    ("5. CONTINUOUS IMPROVEMENT", "FMEA risk scoring (RPN = S*O*D) and Deming PDCA cycles eliminate recurring issues.", Inches(10.4), DANGER),
]

for title, text, left, col in viva_steps:
    add_card(slide9, left, Inches(2.0), Inches(2.1), Inches(4.5), title=title, border_color=col)
    t_box = slide9.shapes.add_textbox(left + Inches(0.12), Inches(2.8), Inches(1.85), Inches(3.4))
    tf = t_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_WHITE

# =============================================================================
# SLIDE 10: Review 1 — SIPOC Process Flow Diagram
# =============================================================================
slide10 = add_base_slide("SIPOC Process Map: Inventory Lifecycle",
                         "Defining process boundaries: Suppliers -> Inputs -> Process -> Outputs -> Customers",
                         "Review 1 — Setup & SRS")

if (screenshots_dir / "sipoc_workflow.png").exists():
    slide10.shapes.add_picture(str(screenshots_dir / "sipoc_workflow.png"), Inches(1.2), Inches(1.8), Inches(10.9), Inches(4.8))

# =============================================================================
# SLIDE 11: Review 1 — Modular Folder Architecture
# =============================================================================
slide11 = add_base_slide("Modular Folder Architecture & SoC Design",
                         "Strict Separation of Concerns: Presentation, Business Logic, and SQLite Storage",
                         "Review 1 — Setup & SRS")

add_card(slide11, Inches(0.8), Inches(1.8), Inches(5.5), Inches(4.8), title="DIRECTORY STRUCTURE", border_color=PRIMARY)
t_box11a = slide11.shapes.add_textbox(Inches(1.0), Inches(2.3), Inches(5.1), Inches(4.2))
tf11a = t_box11a.text_frame
tf11a.word_wrap = True
tree_text = (
    "Inventory_TQM_Project/\n"
    "├── main.py              # Application entry point\n"
    "├── app/\n"
    "│   ├── config.py        # System paths & master categories\n"
    "│   ├── database/        # connection.py (WAL, FK) & schema.py\n"
    "│   ├── models/          # product, audit_log, movement, tqm\n"
    "│   ├── services/        # product, inventory, audit, tqm\n"
    "│   ├── ui/              # app_window, theme, components, views\n"
    "│   └── utils/           # validators (Poka-Yoke) & logger\n"
    "├── tests/               # 42 automated pytest test cases\n"
    "└── docs/                # 11 comprehensive TQM documents\n"
)
p11 = tf11a.paragraphs[0]
p11.text = tree_text
p11.font.size = Pt(9.5)
p11.font.name = "Consolas"
p11.font.color.rgb = ACCENT_BLUE

add_card(slide11, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.8), title="THE GOLDEN ARCHITECTURE RULE", border_color=SUCCESS)
t_box11b = slide11.shapes.add_textbox(Inches(7.0), Inches(2.4), Inches(5.3), Inches(4.0))
tf11b = t_box11b.text_frame
tf11b.word_wrap = True
rules = [
    "THE SCREEN MUST NEVER TALK TO THE DATABASE:",
    "UI Layer (CTk) -> Service Layer -> Model / Database",
    "• No SQL queries inside view files (UI only presents and asks).",
    "• Services hold business rules (stock math, SKU uniqueness, diffs).",
    "• Validators stop bad data at the front door before DB is touched.",
    "• Database layer manages connections, transactions, and foreign keys.",
    "• Benefits for Viva: Easy to explain, easy to debug, high marks for modularity.",
]
for idx, r_text in enumerate(rules):
    p = tf11b.paragraphs[0] if idx == 0 else tf11b.add_paragraph()
    p.text = r_text
    p.font.size = Pt(11)
    p.font.bold = (idx in (0, 1))
    p.font.color.rgb = ACCENT_BLUE if idx in (0, 1) else TEXT_WHITE
    p.space_after = Pt(8)

# =============================================================================
# SLIDE 12: Review 1 — Database Design & Relational Schema
# =============================================================================
slide12 = add_base_slide("Database Design: Relational Schema & Integrity",
                         "SQLite3 with WAL mode, foreign key enforcement, and check constraints",
                         "Review 1 — Setup & SRS")

db_tables = [
    ("products", "product_id (UK), name, category, sku (UK), quantity CHECK(>=0), unit_price CHECK(>0), reorder_level, supplier_name, timestamps", PRIMARY, Inches(0.8), Inches(1.8)),
    ("stock_movements", "id, product_id (FK), movement_type (IN/OUT/ADJUSTMENT/INITIAL), quantity_change, previous_quantity, new_quantity CHECK(>=0), reason, timestamp", SUCCESS, Inches(6.8), Inches(1.8)),
    ("audit_logs (Q07)", "id, entity_type, entity_id, action (CREATE/UPDATE/DELETE/STOCK_ADJUSTMENT), old_values (JSON), new_values (JSON), reason, timestamp", WARNING, Inches(0.8), Inches(3.4)),
    ("defects (Checksheet)", "id, defect_code (UK), category, description, severity (Low/Med/High/Critical), occurrence_count, status, corrective_action, dates", DANGER, Inches(6.8), Inches(3.4)),
    ("fmea_items", "id, process_step, failure_mode, failure_effect, potential_cause, controls, severity (1-10), occurrence (1-10), detection (1-10), rpn (S*O*D), action, owner", ACCENT_BLUE, Inches(0.8), Inches(5.0)),
    ("pdca_records", "id, title, stage (PLAN/DO/CHECK/ACT), problem_statement, plan_description, do_action, expected_result, actual_result, verification, standardization, owner", RGBColor(168, 85, 247), Inches(6.8), Inches(5.0)),
]

for title, desc, col, left, top in db_tables:
    add_card(slide12, left, top, Inches(5.7), Inches(1.4), title=f"TABLE: {title}", border_color=col)
    t_box = slide12.shapes.add_textbox(left + Inches(0.15), top + Inches(0.45), Inches(5.4), Inches(0.85))
    tf = t_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = desc
    p.font.size = Pt(9.5)
    p.font.color.rgb = TEXT_WHITE

# =============================================================================
# SLIDE 13: Review 2 — Working Application & Executive Dashboard
# =============================================================================
slide13 = add_base_slide("Review 2: Working Application & Dashboard",
                         "Live SQLite relational metrics, dynamic KPI cards, and recent audit activity feed",
                         "Review 2 — CRUD & Core Features")

if (screenshots_dir / "dashboard_ui_overview.png").exists():
    slide13.shapes.add_picture(str(screenshots_dir / "dashboard_ui_overview.png"), Inches(1.5), Inches(1.8), Inches(10.3), Inches(4.8))

# =============================================================================
# SLIDE 14: Review 2 — Category Valuation Breakdown (Animated & Interactive)
# =============================================================================
slide14 = add_base_slide("Animated Category Valuation Breakdown Chart",
                         "Smooth cubic ease-out growth animation and interactive hover tooltips",
                         "Review 2 — CRUD & Core Features")

if (screenshots_dir / "category_valuation_chart.png").exists():
    slide14.shapes.add_picture(str(screenshots_dir / "category_valuation_chart.png"), Inches(0.8), Inches(1.8), Inches(7.5), Inches(4.8))

add_card(slide14, Inches(8.6), Inches(1.8), Inches(3.9), Inches(4.8), title="CHART INNOVATIONS", border_color=ACCENT_BLUE)
t_box14 = slide14.shapes.add_textbox(Inches(8.8), Inches(2.4), Inches(3.5), Inches(4.0))
tf14 = t_box14.text_frame
tf14.word_wrap = True
features_14 = [
    "Cubic Ease-Out Growth: Bars animate smoothly from height 0 on dashboard load and refresh.",
    "Interactive Hover Tooltips: Moving cursor over any bar reveals exact valuation ($), percentage share, and inventory counts.",
    "Visual Bar Highlighting: Hovered bar illuminates while other bars softly dim for focus.",
    "Dynamic SQLite Updates: Chart recalculates valuation automatically after every stock adjustment.",
]
for f in features_14:
    p = tf14.add_paragraph()
    p.text = "• " + f
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_WHITE
    p.space_after = Pt(10)

# =============================================================================
# SLIDE 15: Review 2 — CRUD Operations & Poka-Yoke Input Masking
# =============================================================================
slide15 = add_base_slide("Product Catalog CRUD & Input Masking (Q07)",
                         "Enforcing data accuracy at the source through automated input gates",
                         "Review 2 — CRUD & Core Features")

if (screenshots_dir / "crud_poka_yoke_flow.png").exists():
    slide15.shapes.add_picture(str(screenshots_dir / "crud_poka_yoke_flow.png"), Inches(1.2), Inches(1.8), Inches(10.9), Inches(4.8))

# =============================================================================
# SLIDE 16: Review 2 — Audited Stock Adjustments & Movement Ledger
# =============================================================================
slide16 = add_base_slide("Audited Stock Adjustments & Movement Ledger",
                         "Formula: Valuation = Sum(Qty * Price) • Mandatory Reasons & Confirmation Modals",
                         "Review 2 — CRUD & Core Features")

add_card(slide16, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8), title="STOCK ADJUSTMENT WIZARD", border_color=WARNING)
t_box16a = slide16.shapes.add_textbox(Inches(1.0), Inches(2.4), Inches(5.2), Inches(4.0))
tf16a = t_box16a.text_frame
tf16a.word_wrap = True
wizard_pts = [
    "1. Product Selection: Pick product via autocomplete or dropdown.",
    "2. Verified Physical Count: Enter new count (Integer >= 0).",
    "3. Live Variance Preview: System displays real-time delta (+/- units) with color indicators (green for receipt, red for write-off).",
    "4. Mandatory Audit Reason: Controlled selection from standard reasons (Audit Correction, Damaged Write-off, Customer Return).",
    "5. Confirmation Modal: Displays before/after summary before DB commit.",
]
for pt in wizard_pts:
    p = tf16a.add_paragraph()
    p.text = pt
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_WHITE
    p.space_after = Pt(10)

add_card(slide16, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.8), title="DISCRETE STOCK MOVEMENTS LEDGER", border_color=SUCCESS)
t_box16b = slide16.shapes.add_textbox(Inches(7.0), Inches(2.4), Inches(5.3), Inches(4.0))
tf16b = t_box16b.text_frame
tf16b.word_wrap = True
ledger_pts = [
    "Complete Historical Movement Ledger:",
    "• INITIAL: Initial stock baseline loading.",
    "• IN: Stock receipt and upward audit corrections.",
    "• OUT: Damaged write-off, disposal, internal dispatch.",
    "• ADJUSTMENT: Verified cycle count reconciliation.",
    "Immutable Record Attributes: Timestamp (UTC), Product ID, Movement Type, Quantity Delta, Previous Qty, New Qty, and Reason.",
    "Zero Orphaned Records: Foreign key cascade guarantees data integrity.",
]
for pt in ledger_pts:
    p = tf16b.add_paragraph()
    p.text = pt
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_WHITE
    p.space_after = Pt(10)

# =============================================================================
# SLIDE 17: Review 2 — Transactional Audit History (Q07 Feature 5)
# =============================================================================
slide17 = add_base_slide("Immutable Transactional Audit Trail (Q07)",
                         "Dedicated audit_logs table storing structured JSON snapshots of old & new values",
                         "Review 2 — CRUD & Core Features")

add_card(slide17, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8), title="AUDIT LOG ARCHITECTURE", border_color=PRIMARY)
t_box17a = slide17.shapes.add_textbox(Inches(1.0), Inches(2.4), Inches(5.2), Inches(4.0))
tf17a = t_box17a.text_frame
tf17a.word_wrap = True
audit_pts = [
    "Dedicated Table: audit_logs (id, entity_type, entity_id, action, old_values, new_values, reason, timestamp).",
    "Actions Captured: CREATE, UPDATE, DELETE, and STOCK_ADJUSTMENT.",
    "Atomic Multi-Table Commit: The product modification and audit log are saved in the same SQLite transaction.",
    "Rollback Guarantee: If audit write fails, product write rolls back. Zero untracked changes.",
    "Read-Only Protection: No edit or delete controls exposed to users in the GUI.",
]
for pt in audit_pts:
    p = tf17a.add_paragraph()
    p.text = "• " + pt
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_WHITE
    p.space_after = Pt(10)

add_card(slide17, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.8), title="SIDE-BY-SIDE JSON DIFF INSPECTOR", border_color=SUCCESS)
t_box17b = slide17.shapes.add_textbox(Inches(7.0), Inches(2.4), Inches(5.3), Inches(4.0))
tf17b = t_box17b.text_frame
tf17b.word_wrap = True
diff_demo = (
    "PREVIOUS VALUES (OLD - JSON):\n"
    "{\n"
    '  "quantity": 35,\n'
    '  "unit_price": 1250.00\n'
    "}\n\n"
    "APPLIED VALUES (NEW - JSON):\n"
    "{\n"
    '  "quantity": 45,\n'
    '  "unit_price": 1300.00\n'
    "}\n\n"
    "Reason: Supplier price adjustment and audit count"
)
p17 = tf17b.paragraphs[0]
p17.text = diff_demo
p17.font.size = Pt(10)
p17.font.name = "Consolas"
p17.font.color.rgb = ACCENT_BLUE

# =============================================================================
# SLIDE 18: TQM Suite — Critical to Quality (CTQ) Scorecard
# =============================================================================
slide18 = add_base_slide("Critical to Quality (CTQ) Scorecard",
                         "Live compliance verification across 5 measurable data accuracy characteristics",
                         "TQM Quality & Analytics Suite")

if (screenshots_dir / "ctq_scorecard.png").exists():
    slide18.shapes.add_picture(str(screenshots_dir / "ctq_scorecard.png"), Inches(0.8), Inches(1.8), Inches(7.5), Inches(4.8))

add_card(slide18, Inches(8.6), Inches(1.8), Inches(3.9), Inches(4.8), title="CTQ METRICS HIGHLIGHTS", border_color=SUCCESS)
t_box18 = slide18.shapes.add_textbox(Inches(8.8), Inches(2.4), Inches(3.5), Inches(4.0))
tf18 = t_box18.text_frame
tf18.word_wrap = True
ctq_pts = [
    "CTQ-1: Stock Quantity Integrity -> 100% Non-negative integer compliance [PASS]",
    "CTQ-2: Identifier Uniqueness -> 100% Unique SKU ratio across all catalog items [PASS]",
    "CTQ-3: Data Completeness -> 100% Zero blank mandatory fields [PASS]",
    "CTQ-4: Category Standardization -> 100% Conformance to 6 master taxonomies [PASS]",
    "CTQ-5: Audit Traceability -> >= 100% Transactional change coverage [PASS]",
]
for pt in ctq_pts:
    p = tf18.add_paragraph()
    p.text = pt
    p.font.size = Pt(10.5)
    p.font.color.rgb = TEXT_WHITE
    p.space_after = Pt(10)

# =============================================================================
# SLIDE 19: TQM Suite — Pareto Defect Analysis (80/20 Rule)
# =============================================================================
slide19 = add_base_slide("TQM Pareto Analysis (80/20 Rule)",
                         "Prioritizing the vital few defect root causes using empirical checksheet data",
                         "TQM Quality & Analytics Suite")

if (screenshots_dir / "pareto_analysis_chart.png").exists():
    slide19.shapes.add_picture(str(screenshots_dir / "pareto_analysis_chart.png"), Inches(0.8), Inches(1.8), Inches(7.5), Inches(4.8))

add_card(slide19, Inches(8.6), Inches(1.8), Inches(3.9), Inches(4.8), title="THE 80/20 PRINCIPLE", border_color=PRIMARY)
t_box19 = slide19.shapes.add_textbox(Inches(8.8), Inches(2.4), Inches(3.5), Inches(4.0))
tf19 = t_box19.text_frame
tf19.word_wrap = True
pareto_pts = [
    "Vital Few Identified: Invalid Input (28) and Stock Mismatch (19) account for 62% of historical errors.",
    "80% Cutoff Threshold: Green dashed reference line separates vital root causes from useful many.",
    "Interactive Tooltips: Hovering over bars displays exact frequencies, cumulative %, and classification.",
    "Closed Quality Loop: Defect checksheets directly feed Pareto chart, focusing engineering remediation.",
]
for pt in pareto_pts:
    p = tf19.add_paragraph()
    p.text = pt
    p.font.size = Pt(10.5)
    p.font.color.rgb = TEXT_WHITE
    p.space_after = Pt(10)

# =============================================================================
# SLIDE 20: TQM Suite — Ishikawa (Fishbone) 4M Cause-and-Effect
# =============================================================================
slide20 = add_base_slide("Ishikawa (Fishbone) 4M Cause-and-Effect Analysis",
                         "Systematic root-cause exploration across People, Process, Software Code, and Infrastructure",
                         "TQM Quality & Analytics Suite")

if (screenshots_dir / "fishbone_diagram.png").exists():
    slide20.shapes.add_picture(str(screenshots_dir / "fishbone_diagram.png"), Inches(1.2), Inches(1.8), Inches(10.9), Inches(4.8))

# =============================================================================
# SLIDE 21: TQM Suite — FMEA Worksheet & 95% RPN Risk Reduction
# =============================================================================
slide21 = add_base_slide("Failure Mode and Effects Analysis (FMEA)",
                         "Formula: RPN = Severity * Occurrence * Detection (1-10 Scale)",
                         "TQM Quality & Analytics Suite")

table_shape21 = slide21.shapes.add_table(6, 6, Inches(0.8), Inches(1.8), Inches(11.7), Inches(4.8))
tbl21 = table_shape21.table
tbl21.columns[0].width = Inches(2.5)
tbl21.columns[1].width = Inches(2.2)
tbl21.columns[2].width = Inches(1.3)
tbl21.columns[3].width = Inches(2.9)
tbl21.columns[4].width = Inches(1.3)
tbl21.columns[5].width = Inches(1.5)

fmea_headers = ["Process Step", "Potential Failure Mode", "Pre RPN", "Q07 Poka-Yoke Safeguard", "Post RPN", "Risk Drop"]
for i, h in enumerate(fmea_headers):
    cell = tbl21.cell(0, i)
    cell.fill.solid()
    cell.fill.fore_color.rgb = PRIMARY
    p = cell.text_frame.paragraphs[0]
    p.text = h
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = TEXT_WHITE

fmea_rows = [
    ("Product Registration", "Malformed SKU Code", "252 (High)", "Regex Mask & SQLite UNIQUE check", "7 (Low)", "-97.2%"),
    ("Stock Receipt", "Negative Quantity Entry", "200 (High)", "Integer parser & SQLite CHECK (qty>=0)", "8 (Low)", "-96.0%"),
    ("Category Assignment", "Spelling Inconsistency", "175 (Med)", "Controlled 6-category dropdown", "5 (Low)", "-97.1%"),
    ("Product Deletion", "Accidental Catalog Delete", "162 (Med)", "Confirmation modal with item summary", "18 (Low)", "-88.9%"),
    ("Stock Adjustment", "Unaccounted Variance", "128 (Med)", "Mandatory reason & JSON audit diff", "8 (Low)", "-93.8%"),
]

for row_idx, r_data in enumerate(fmea_rows, start=1):
    for col_idx, text in enumerate(r_data):
        cell = tbl21.cell(row_idx, col_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = CARD_BG if row_idx % 2 == 0 else RGBColor(24, 34, 53)
        p = cell.text_frame.paragraphs[0]
        p.text = text
        p.font.size = Pt(9.5)
        p.font.color.rgb = TEXT_WHITE if col_idx != 4 else SUCCESS
        if col_idx in (2, 4, 5):
            p.font.bold = True

# =============================================================================
# SLIDE 22: TQM Suite — How Audit Logs Feed FMEA & Deming PDCA Cycle
# =============================================================================
slide22 = add_base_slide("The Closed Quality Loop: Logs -> FMEA -> PDCA",
                         "Connecting daily operational transactions with Deming continuous improvement",
                         "TQM Quality & Analytics Suite")

steps22 = [
    ("1. USER ACTION", "Clerk enters data or executes stock adjustment.", PRIMARY, Inches(0.8)),
    ("2. LOG EMISSION", "audit_logs and defects record event & validation rejects.", WARNING, Inches(3.85)),
    ("3. STATISTICAL ANALYSIS", "Pareto 80/20 & CTQ Scorecard aggregate defect frequencies.", SUCCESS, Inches(6.90)),
    ("4. PDCA CONTINUOUS CYCLE", "PLAN, DO, CHECK, ACT cycles standardize architectural safeguards.", ACCENT_BLUE, Inches(9.95)),
]

for title, desc, col, left in steps22:
    add_card(slide22, left, Inches(1.8), Inches(2.6), Inches(2.2), title=title, border_color=col)
    t_box = slide22.shapes.add_textbox(left + Inches(0.15), Inches(2.4), Inches(2.3), Inches(1.4))
    tf = t_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = desc
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_WHITE

add_card(slide22, Inches(0.8), Inches(4.3), Inches(11.7), Inches(2.4), title="PDCA 4-STAGE CONTINUOUS IMPROVEMENT IN PRACTICE", border_color=SUCCESS)
t_box22b = slide22.shapes.add_textbox(Inches(1.0), Inches(4.8), Inches(11.3), Inches(1.8))
tf22b = t_box22b.text_frame
tf22b.word_wrap = True
pdca_pts = [
    "• PLAN: Identify high rate of input typos and duplicate SKUs causing stock variances.",
    "• DO: Implement ProductValidator regex masking and controlled Category OptionMenu dropdown.",
    "• CHECK: Verify 100% rejection rate in automated pytest suite and inspect zero duplicate entries in live audit logs.",
    "• ACT: Standardize ProductValidator as mandatory gatekeeper for all data endpoints across system.",
]
for pt in pdca_pts:
    p = tf22b.add_paragraph()
    p.text = pt
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_WHITE
    p.space_after = Pt(4)

# =============================================================================
# SLIDE 23: Review 2 — Automated Testing & Data Quality Verification
# =============================================================================
slide23 = add_base_slide("Automated Testing & Data Quality Verification",
                         "Comprehensive pytest test suite guaranteeing reliability and zero regression",
                         "Review 2 — CRUD & Core Features")

test_cards = [
    ("42 / 42 PASSED (100%)", "Complete automated test suite passing in 0.58 seconds with zero failures.", SUCCESS, Inches(0.8), Inches(1.8)),
    ("ZERO TEST POLLUTION", "Tests run on ephemeral temporary SQLite databases via pytest tmp_path fixture.", PRIMARY, Inches(6.8), Inches(1.8)),
    ("POKA-YOKE BOUNDARIES", "Extensive test coverage of negative numbers, invalid strings, malformed SKUs.", WARNING, Inches(0.8), Inches(4.3)),
    ("ACID ROLLBACK PROVEN", "Verified that failed multi-table transactions roll back both data and audit rows.", ACCENT_BLUE, Inches(6.8), Inches(4.3)),
]

for title, desc, col, left, top in test_cards:
    add_card(slide23, left, top, Inches(5.7), Inches(2.2), title=title, border_color=col)
    t_box = slide23.shapes.add_textbox(left + Inches(0.2), top + Inches(0.6), Inches(5.3), Inches(1.4))
    tf = t_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = desc
    p.font.size = Pt(12)
    p.font.color.rgb = TEXT_WHITE

# =============================================================================
# SLIDE 24: Viva Summary & "The Golden Sentence"
# =============================================================================
slide24 = add_base_slide("Summary & The Golden Viva Takeaway",
                         "The master summary sentence that synthesizes the entire engineering achievement",
                         "Viva Voce Defense Summary")

add_card(slide24, Inches(0.8), Inches(1.8), Inches(11.7), Inches(2.4), title="THE GOLDEN SENTENCE FOR VIVA", border_color=SUCCESS)
t_box24a = slide24.shapes.add_textbox(Inches(1.0), Inches(2.4), Inches(11.3), Inches(1.6))
tf24a = t_box24a.text_frame
tf24a.word_wrap = True
p24a = tf24a.paragraphs[0]
p24a.text = (
    '"The UI never writes SQL.\n'
    'Poka-Yoke validation stops bad data at the front gate.\n'
    'Every catalog and stock change is transactionally audited in JSON.\n'
    'And operational logs continuously feed live Pareto, FMEA, and PDCA continuous improvement."'
)
p24a.font.size = Pt(15)
p24a.font.bold = True
p24a.font.color.rgb = ACCENT_BLUE

add_card(slide24, Inches(0.8), Inches(4.5), Inches(11.7), Inches(2.2), title="PROJECT DELIVERABLES CHECKLIST", border_color=PRIMARY)
t_box24b = slide24.shapes.add_textbox(Inches(1.0), Inches(5.0), Inches(11.3), Inches(1.5))
tf24b = t_box24b.text_frame
tf24b.word_wrap = True
chk_pts = (
    "✓ Working Python Desktop Application (CustomTkinter + SQLite3 + Matplotlib)\n"
    "✓ All 5 Mandatory Q07 Features Implemented & Tested\n"
    "✓ 42 Automated pytest test cases passing in 0.58s\n"
    "✓ 11 Complete Documentation Deliverables (SRS, Architecture, DB Design, SIPOC, FMEA, CTQ, PDCA, Manual)\n"
    "✓ Clean Git Repository pushed to GitHub: https://github.com/dheeraj0204/Inventory-Management-System"
)
p24b = tf24b.paragraphs[0]
p24b.text = chk_pts
p24b.font.size = Pt(11)
p24b.font.color.rgb = TEXT_WHITE

# Save PowerPoint presentation
output_pptx_path = Path("docs/BBAT104_TQM_Q07_Review1_Review2_Presentation.pptx")
prs.save(str(output_pptx_path))
print(f"Presentation saved successfully to: {output_pptx_path}")
