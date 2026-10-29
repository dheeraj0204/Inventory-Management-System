"""
BBAT104 - Fundamentals of Total Quality Management
Q07: Improve Data Accuracy
Script to generate the complete Viva Defense Handbook in PDF format.
"""

import sys
import os
import textwrap
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.patches as patches

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PDF = PROJECT_ROOT / "docs" / "BBAT104_TQM_Q07_Viva_Defense_Handbook.pdf"

class PDFDocBuilder:
    def __init__(self, filename):
        self.filename = filename
        self.pdf = PdfPages(filename)
        self.fig = None
        self.ax = None
        self.current_y = 10.1
        self.current_page = 0
        self.total_pages_placeholder = 12
        self.pages = []

    def start_new_page(self, section_title="REVIEW 1 & 2 VIVA DEFENSE GUIDE"):
        if self.fig:
            self.pdf.savefig(self.fig, dpi=150)
            plt.close(self.fig)
            
        self.current_page += 1
        self.fig = plt.figure(figsize=(8.27, 11.69))  # A4 Portrait
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.set_xlim(0, 8.27)
        self.ax.set_ylim(0, 11.69)
        self.ax.axis('off')

        # Header Banner (Navy)
        banner = patches.Rectangle((0, 10.69), 8.27, 1.0, facecolor='#0F172A', edgecolor='none')
        self.ax.add_patch(banner)
        
        # Gold accent line under banner
        accent_line = patches.Rectangle((0, 10.66), 8.27, 0.03, facecolor='#F59E0B', edgecolor='none')
        self.ax.add_patch(accent_line)

        # Header Text
        self.ax.text(0.6, 11.35, "BBAT104 • FUNDAMENTALS OF TOTAL QUALITY MANAGEMENT", fontsize=9.5, fontweight='bold', color='#38BDF8', fontfamily='sans-serif')
        self.ax.text(0.6, 11.02, "INVENTORY IMS — Q07: IMPROVE DATA ACCURACY", fontsize=13, fontweight='bold', color='#FFFFFF', fontfamily='sans-serif')
        self.ax.text(0.6, 10.77, f"Student: Dheeraj Khetwal  |  Session 2026-27  |  {section_title}", fontsize=8.5, color='#94A3B8', fontfamily='sans-serif')

        # Footer
        footer_line = patches.Rectangle((0.6, 0.55), 7.07, 0.01, facecolor='#E2E8F0', edgecolor='none')
        self.ax.add_patch(footer_line)
        self.ax.text(0.6, 0.38, "Academic Session 2026–27  •  Dheeraj Khetwal  •  BBAT104 TQM Q07", fontsize=8, color='#64748B', fontfamily='sans-serif')
        self.ax.text(7.67, 0.38, f"Page {self.current_page} of 9", fontsize=8, fontweight='bold', color='#0F172A', ha='right', fontfamily='sans-serif')

        self.current_y = 10.25

    def check_space(self, height_needed, section_title="REVIEW 1 & 2 VIVA DEFENSE GUIDE"):
        if self.current_y - height_needed < 0.8:
            self.start_new_page(section_title)

    def draw_section_heading(self, title, subtitle=None):
        self.check_space(0.8)
        # Ribbon banner
        ribbon = patches.FancyBboxPatch((0.6, self.current_y - 0.38), 7.07, 0.38, boxstyle="round,pad=0.04,rounding_size=0.06", facecolor='#1E293B', edgecolor='none')
        self.ax.add_patch(ribbon)
        self.ax.text(0.75, self.current_y - 0.24, title, fontsize=10.5, fontweight='bold', color='#F8FAFC', fontfamily='sans-serif')
        
        self.current_y -= 0.50
        if subtitle:
            self.ax.text(0.65, self.current_y, subtitle, fontsize=8.5, fontstyle='italic', color='#475569', fontfamily='sans-serif')
            self.current_y -= 0.22

    def draw_card(self, title, content_lines, accent_color='#2563EB', tag=None, extra_note=None):
        # Calculate height based on lines
        total_wrapped_lines = 0
        wrapped_paragraphs = []
        for p in content_lines:
            wrapped = textwrap.wrap(p, width=82)
            wrapped_paragraphs.append(wrapped)
            total_wrapped_lines += len(wrapped)
            
        card_height = 0.40 + (total_wrapped_lines * 0.175)
        if extra_note:
            note_wrapped = textwrap.wrap(extra_note, width=82)
            card_height += 0.20 + (len(note_wrapped) * 0.16)

        self.check_space(card_height + 0.15)

        card_y = self.current_y - card_height
        card = patches.FancyBboxPatch((0.6, card_y), 7.07, card_height, boxstyle="round,pad=0.05,rounding_size=0.08", facecolor='#F8FAFC', edgecolor='#E2E8F0', linewidth=1)
        self.ax.add_patch(card)

        # Left accent stripe
        accent = patches.Rectangle((0.6, card_y), 0.08, card_height, facecolor=accent_color, edgecolor='none')
        self.ax.add_patch(accent)

        # Title & Tag
        self.ax.text(0.80, self.current_y - 0.22, title, fontsize=10, fontweight='bold', color='#0F172A', fontfamily='sans-serif')
        if tag:
            tag_box = patches.FancyBboxPatch((6.4, self.current_y - 0.26), 1.15, 0.18, boxstyle="round,pad=0.02,rounding_size=0.04", facecolor=accent_color, edgecolor='none')
            self.ax.add_patch(tag_box)
            self.ax.text(6.975, self.current_y - 0.17, tag, fontsize=7.5, fontweight='bold', color='#FFFFFF', ha='center', fontfamily='sans-serif')

        # Content text
        text_y = self.current_y - 0.42
        for para in wrapped_paragraphs:
            for line in para:
                self.ax.text(0.80, text_y, line, fontsize=8.8, color='#334155', fontfamily='sans-serif', linespacing=1.2)
                text_y -= 0.175
            text_y -= 0.05

        if extra_note:
            text_y -= 0.05
            self.ax.text(0.80, text_y, "[KEY VIVA TAKEAWAY]:", fontsize=8, fontweight='bold', color=accent_color, fontfamily='sans-serif')
            text_y -= 0.16
            for line in note_wrapped:
                self.ax.text(0.80, text_y, line, fontsize=8.2, fontstyle='italic', color='#1E293B', fontfamily='sans-serif')
                text_y -= 0.16

        self.current_y = card_y - 0.18

    def draw_qa_card(self, q_num, question, answer_points, key_formula=None):
        total_wrapped_lines = 0
        wrapped_q = textwrap.wrap(f"Q{q_num}: \"{question}\"", width=76)
        
        wrapped_paras = []
        for p in answer_points:
            wrapped = textwrap.wrap(p, width=78)
            wrapped_paras.append(wrapped)
            total_wrapped_lines += len(wrapped)

        card_height = 0.40 + (len(wrapped_q) * 0.20) + (total_wrapped_lines * 0.175) + (0.25 if key_formula else 0.0)
        self.check_space(card_height + 0.15)

        card_y = self.current_y - card_height
        card = patches.FancyBboxPatch((0.6, card_y), 7.07, card_height, boxstyle="round,pad=0.05,rounding_size=0.08", facecolor='#F1F5F9', edgecolor='#CBD5E1', linewidth=1)
        self.ax.add_patch(card)

        # Accent bar in Amber/Red
        accent = patches.Rectangle((0.6, card_y), 0.10, card_height, facecolor='#DC2626', edgecolor='none')
        self.ax.add_patch(accent)

        # Question header
        text_y = self.current_y - 0.22
        for line in wrapped_q:
            self.ax.text(0.82, text_y, line, fontsize=9.5, fontweight='bold', color='#991B1B', fontfamily='sans-serif')
            text_y -= 0.20

        text_y -= 0.05
        # Answer points
        for para in wrapped_paras:
            for line in para:
                self.ax.text(0.82, text_y, line, fontsize=8.6, color='#1E293B', fontfamily='sans-serif')
                text_y -= 0.175
            text_y -= 0.04

        if key_formula:
            self.ax.text(0.82, text_y, f"[RULE/FORMULA]: {key_formula}", fontsize=8.2, fontweight='bold', color='#2563EB', fontfamily='sans-serif')

        self.current_y = card_y - 0.18

    def close(self):
        if self.fig:
            self.pdf.savefig(self.fig, dpi=150)
            plt.close(self.fig)
        self.pdf.close()
        print(f"PDF successfully generated with {self.current_page} pages at: {self.filename}")

def build_pdf():
    os.makedirs(OUTPUT_PDF.parent, exist_ok=True)
    builder = PDFDocBuilder(str(OUTPUT_PDF))

    # ==========================================
    # PAGE 1: TITLE & PROTOTYPE ELEVATOR PITCH
    # ==========================================
    builder.start_new_page("OVERVIEW & ELEVATOR PITCH")
    
    builder.draw_section_heading("PART 1: 1-PARAGRAPH PROTOTYPE PITCH (ELEVATOR SCRIPT)", "Word-for-word spoken pitch to deliver when evaluators ask for an overview.")
    
    pitch_lines = [
        "\"Good morning Sir/Ma'am. Mera project Inventory Management System hai jisme mujhe assigned quality goal Q07: Improve Data Accuracy mila tha. Industry mein lagbhag 60% inventory errors downstream discovery ke time 10x se 100x zyada costly ho jaate hain.",
        "Is problem ko solve karne ke liye maine Python, CustomTkinter aur SQLite (WAL Mode) par ek enterprise desktop application develop ki hai jo Philip Crosby ke 'Zero Defect' aur Shigeo Shingo ke 'Poka-Yoke' principles par based hai.",
        "Hamara system data save hone se pehle hi invalid entries ko 3-tier validation gates par reject karta hai, har stock movement aur update ka immutable JSON audit trail capture karta hai, aur live CTQ Scorecard, Pareto 80/20 Analysis aur FMEA Matrix ke through continuous quality improvement ensure karta hai.",
        "Poora system 42/42 automated pytest tests se verified hai aur code strictly 'Screen Never Writes SQL' clean architecture follow karta hai.\""
    ]
    builder.draw_card("ELEVATOR SCRIPT — WHAT TO SPEAK TO EVALUATORS", pitch_lines, accent_color='#2563EB', tag="CORE PITCH", 
                      extra_note="Yeh paragraph 40-50 seconds mein bolna hai. Isme technology, TQM philosophers (Crosby & Shingo), architecture aur 42/42 tests sab cover ho jaate hain.")

    builder.draw_section_heading("CORE TQM ACADEMIC FOUNDATIONS", "Key theoretical alignments connecting software to syllabus.")
    
    tqm_foundations = [
        "• Philip Crosby (Zero Defects): Prevention is cheaper than inspection. Fixing errors at input costs 1/10th of post-dispatch corrections.",
        "• Shigeo Shingo (Poka-Yoke): Source inspection at the point of entry. Eliminating inadvertent operator slips before persistence.",
        "• Walter Shewhart & W.E. Deming (SPC): Measuring process variation and applying Plan-Do-Check-Act (PDCA) to software rules.",
        "• Joseph Juran (Pareto 80/20): Concentrating engineering effort on the 'vital few' defect categories causing 80% of data errors."
    ]
    builder.draw_card("ACADEMIC THEORIES APPLIED IN THIS PROJECT", tqm_foundations, accent_color='#16A34A', tag="TQM ROOTS")

    # ==========================================
    # PAGES 2 TO 5: REVIEW 1 (SLIDES 1 TO 13)
    # ==========================================
    builder.start_new_page("REVIEW 1: PROCESS, SRS & DESIGN")
    builder.draw_section_heading("PART 2: REVIEW 1 SLIDE-WISE EXPLANATION (SLIDES 1 TO 13)", "What to speak for each slide in Review 1.")

    # Slide 1
    builder.draw_card("SLIDE 01: TITLE & ACADEMIC IDENTITY", [
        "Kya bolna hai: 'Sir, yeh mera BBAT104 ka Review 1 & 2 presentation hai. Mera topic hai Enterprise Inventory Management System aur focus goal hai Q07: Improve Data Accuracy. Humne isme core focus Quality at the Gate par rakha hai: Prevent -> Record -> Improve.'",
        "Stack: Python 3.11+, CustomTkinter desktop UI, SQLite3 (WAL mode), Matplotlib SQC charts, pytest."
    ], accent_color='#0F172A', tag="SLIDE 01")

    # Slide 2
    builder.draw_card("SLIDE 02: EXECUTIVE SUMMARY & ACADEMIC VISION", [
        "Kya bolna hai: 'Sir, traditional software mein inspection baad mein hoti hai, jo Philip Crosby ke cost-of-quality rule ke against hai. Agar dispatch ke baad stock error pata chale toh cost 10x se 100x badh jaati hai. Hamari vision hai data enter hote hi defect ko block karna taaki downstream phantom stock aur stockouts 0% ho sakein.'",
        "Key Point: Quality is designed into the workflow, not inspected only at the end."
    ], accent_color='#2563EB', tag="SLIDE 02")

    # Slide 3
    builder.draw_card("SLIDE 03: THREE FOUNDATIONAL QUALITY IDEAS", [
        "Kya bolna hai: 'Humne teen quality pillars integrate kiye hain:",
        "1. Poka-Yoke: Entry par regex, bounds aur controlled dropdowns.",
        "2. Statistical Quality: Pareto 80/20 analysis aur CTQ scorecard.",
        "3. Continuous Auditing: Har change ka structured JSON diff, reason aur timestamp ke sath track hona.'",
        "Cycle: Prevent -> Measure -> Learn -> Prevent Better."
    ], accent_color='#16A34A', tag="SLIDE 03")

    # Slide 4
    builder.draw_card("SLIDE 04: PROBLEM STATEMENT & INDUSTRIAL BASELINE", [
        "Kya bolna hai: 'Sir, manual inventory ka sabse bada risk hai Garbage In, Garbage Out. Users spelling alag likhte hain, negative quantity enter kar dete hain, ya unexplained adjustments karte hain. Isse physical stock aur system stock match nahi hota. Hamara project boundary desktop IMS ke andar data accuracy aur mutation integrity ko enforce karna hai.'",
        "Consequences: Phantom stock, procurement delays, and unreconciled balance sheets."
    ], accent_color='#DC2626', tag="SLIDE 04")

    # Slide 5
    builder.draw_card("SLIDE 05: STAKEHOLDER MATRIX & QUALITY NEEDS (VOC)", [
        "Kya bolna hai: 'TQM mein Voice of Customer (VOC) sabse pehle aati hai:",
        "• Store Manager ko live valuation aur low-stock alert chahiye.",
        "• Procurement Officer ko reliable reorder signals chahiye.",
        "• Auditor ko forensic JSON audit trail chahiye.",
        "• Warehouse Operator ko fast, error-proof input UI chahiye.'",
        "Design Principle: Controls strict hone chahiye data integrity par, par user ke liye clear error message hona chahiye."
    ], accent_color='#7C3AED', tag="SLIDE 05")

    # Slide 6
    builder.draw_card("SLIDE 06: MEASURABLE QUALITY REQUIREMENTS & VIVA METRICS", [
        "Kya bolna hai: 'Sir, humne qualitative claims ke sath verifiable metrics set kiye hain:",
        "• SKU Uniqueness: 100% database constraint + service validation.",
        "• Non-negative stock & positive price: 100% enforced.",
        "• Category taxonomy: Free-text hatakar 100% controlled dropdown.",
        "• Regression testing: 42 out of 42 automated tests pass ho rahe hain.'",
        "Viva Note: Alag se baseline (qualitative) aur post-intervention verified results bataye hain."
    ], accent_color='#0284C7', tag="SLIDE 06")

    # Slide 7
    builder.draw_card("SLIDE 07: FIVE MEASURABLE QUALITY OBJECTIVES (O1 TO O5)", [
        "Kya bolna hai: 'Hamare 5 testable objectives hain:",
        "• O1: Entry gate par invalid SKU aur category reject karna.",
        "• O2: Quantity >= 0 aur Price > 0 invariants protect karna.",
        "• O3: Har CREATE, UPDATE, DELETE aur adjustment ko JSON diff ke sath log karna.",
        "• O4: Pareto aur CTQ ke through recurring defects prioritize karna.",
        "• O5: 3-tier maintainable architecture maintain karna.'"
    ], accent_color='#D97706', tag="SLIDE 07")

    # Slide 8
    builder.draw_card("SLIDE 08: SYSTEM SCOPE, BOUNDARIES & ROLE-BASED ACCESS", [
        "Kya bolna hai: 'Sir, project ki boundaries defined hain. In-Scope: Desktop CRUD, Stock adjustments, Audit history aur TQM analytics. Out-of-Scope: Multi-tenant cloud aur RFID hardware. Humne principle of least privilege ke under Admin, Manager aur Staff ke role permissions define kiye hain.'"
    ], accent_color='#475569', tag="SLIDE 08")

    # Slide 9
    builder.draw_card("SLIDE 09: Q07 FEATURE SPECIFICATION — 5 POKA-YOKE ENHANCEMENTS", [
        "Kya bolna hai: 'Yeh hamare mandatory 5 Poka-Yoke features hain:",
        "• F1 (Validation): SKU regex, positive numbers, whitespace trim.",
        "• F2 (Controlled Taxonomy): 5 fixed categories, duplicate spelling impossible.",
        "• F3 (Debounced Search): 300ms indexed search, accidental duplicate product create hone se rokta hai.",
        "• F4 (Confirmation Modal): Deletion ya adjustment se pehle item details ka preview popup.",
        "• F5 (JSON Audit History): Atomic change log with old/new state.'"
    ], accent_color='#2563EB', tag="SLIDE 09")

    # Slide 10
    builder.draw_card("SLIDE 10: VIVA MAPPING: FEATURES VS TQM DIMENSIONS", [
        "Kya bolna hai: 'Sir, humne software features ko David Garvin ke 8 Dimensions (Conformance, Reliability, Serviceability) aur Deming ke 14 Principles se map kiya hai. For example, Deming ka Principle 3 hai Build quality into the process, cease mass inspection—yeh hamara Poka-Yoke input gate directly fulfill karta hai.'"
    ], accent_color='#16A34A', tag="SLIDE 10")

    # Slide 11
    builder.draw_card("SLIDE 11: END-TO-END SIPOC PROCESS MAPPING", [
        "Kya bolna hai: 'SIPOC diagram hamari process boundary dikhata hai:",
        "• Suppliers: Vendors aur Warehouse.",
        "• Inputs: SKU, category, purchase orders.",
        "• Process: 5 steps—Validate -> Deduplicate -> Commit Transaction -> Write Audit Diff -> Recalculate CTQ.",
        "• Outputs: Verified records, valuation, alerts.",
        "• Customers: Store Manager, Procurement aur Auditors.'"
    ], accent_color='#0284C7', tag="SLIDE 11")

    # Slide 12
    builder.draw_card("SLIDE 12: ARCHITECTURAL INTEGRITY — SCREEN NEVER WRITES SQL", [
        "Kya bolna hai: 'Sir, hamari clean code rule hai: Screen kabhi direct SQL nahi likhegi.",
        "• Presentation Layer (app/views) sirf service ko call karti hai.",
        "• Service Layer (app/services) business rules aur Poka-Yoke validation run karti hai.",
        "• Persistence Layer (app/repositories) safe parameterized SQL execute karti hai. Isse separation of concerns aur testability guarantee hoti hai.'"
    ], accent_color='#7C3AED', tag="SLIDE 12")

    # Slide 13
    builder.draw_card("SLIDE 13: RELATIONAL DATABASE SCHEMA & ACID INTEGRITY", [
        "Kya bolna hai: 'Hum SQLite ko WAL Mode (Write-Ahead Logging) aur PRAGMA foreign_keys = ON ke sath run karte hain. Database schema mein CHECK(quantity >= 0) aur UNIQUE(sku) lagaya hai. Koi bhi multi-step operation atomic transaction ke andar commit ya rollback hota hai, ensuring ACID compliance.'"
    ], accent_color='#0F172A', tag="SLIDE 13")

    # ==========================================
    # PAGES 6 TO 9: REVIEW 2 (SLIDES 14 TO 24)
    # ==========================================
    builder.start_new_page("REVIEW 2: WORKING APP & TQM TOOLS")
    builder.draw_section_heading("PART 3: REVIEW 2 SLIDE-WISE EXPLANATION (SLIDES 14 TO 24)", "What to speak for working implementation and quality tools.")

    # Slide 14
    builder.draw_card("SLIDE 14: LIVE WORKING IMPLEMENTATION (DASHBOARD)", [
        "Kya bolna hai: 'Sir, yeh hamara live CustomTkinter application hai. Dashboard real-time SQLite se data fetch karta hai: yahan 11 unique products, 634 total units, $328,099 ki total valuation aur 3 low-stock alerts hain. Category Valuation chart interactive hai aur bar par hover karte hi exact valuation aur percentage dikhata hai.'",
        "Visuals: 4 KPI cards, Category Valuation Bar Chart, Recent Audit Activity stream."
    ], accent_color='#2563EB', tag="SLIDE 14")

    # Slide 15
    builder.draw_card("SLIDE 15: FULL CRUD LIFECYCLE WITH 3-TIER POKA-YOKE GATES", [
        "Kya bolna hai: 'Yahan product creation aur edit workflow hai. Jaise hi user Add New Product par click karta hai, modal form khulta hai. Category controlled dropdown se aati hai, SKU auto-format hota hai. Agar koi negative quantity ya empty field daalta hai, toh system save hone se pehle clear warning dialog dikhata hai.'",
        "Path: User Input -> UI Validation -> Service Gate -> SQLite Transaction -> Audit Diff."
    ], accent_color='#16A34A', tag="SLIDE 15")

    # Slide 16
    builder.draw_card("SLIDE 16: STOCK MOVEMENT & INVENTORY VARIANCE MANAGEMENT", [
        "Kya bolna hai: 'Inventory tab mein stock valuation ka formula Sum(Quantity * Unit Price) continuously compute hota hai. Stock adjustment ke liye mandatory reason (jaise Damaged Stock ya Audit Reconciliation) select karna padta hai. Unexplained stock adjustments impossible hain.'",
        "Invariants: Quantity strictly non-negative; low stock alerts trigger automatically when Qty <= Reorder Level."
    ], accent_color='#D97706', tag="SLIDE 16")

    # Slide 17
    builder.draw_card("SLIDE 17: IMMUTABLE AUDIT TRAIL & FORENSIC JSON STATE DIFFING", [
        "Kya bolna hai: 'Sir, yeh hamari forensic audit screen hai. Har row ke aage Inspect JSON button hai. Popup mein hum dekh sakte hain ki purani value kya thi, nayi value kya hui, delta kitna tha, kisne change kiya aur timestamp kya tha. Yeh screen 100% read-only hai, koi bhi user history delete ya edit nahi kar sakta.'",
        "Format: Valid JSON snapshot with old_state, new_state, delta, reason, and UTC timestamp."
    ], accent_color='#7C3AED', tag="SLIDE 17")

    # Slide 18
    builder.draw_card("SLIDE 18: CRITICAL TO QUALITY (CTQ) PERFORMANCE SCORECARD", [
        "Kya bolna hai: 'Six Sigma CTQ methodology ke under humne 5 critical parameters define kiye hain: SKU uniqueness, non-negative stock, price validity, category standard aur audit coverage. System live database scan karke 100% compliance confirm karta hai.'",
        "Target: 100% compliance across all 5 checks. Proves zero defect state in database."
    ], accent_color='#0284C7', tag="SLIDE 18")

    # Slide 19
    builder.draw_card("SLIDE 19: STATISTICAL DEFECT PARETO ANALYSIS — 80/20 RULE", [
        "Kya bolna hai: 'Joseph Juran ke 80/20 rule ke according, humne intercepted entry errors ko Pareto chart par plot kiya hai. Bars descending order mein hain aur red line cumulative percentage dikhati hai. Data prove karta hai ki top 2 causes—Missing Fields aur Invalid Price Format—hi 67.9% defects ke liye responsible hain. Humne Poka-Yoke se sabse pehle inhi Vital Few ko eliminate kiya hai.'",
        "Formula: Cumulative % = (Sum defects 1..k / Total defects) * 100."
    ], accent_color='#DC2626', tag="SLIDE 19")

    # Slide 20
    builder.draw_card("SLIDE 20: 4M CAUSE-AND-EFFECT ANALYSIS (ISHIKAWA FISHBONE)", [
        "Kya bolna hai: 'Inventory inaccuracy ka root cause analyse karne ke liye humne Ishikawa diagram design kiya across 4Ms:",
        "• Man: User fatigue aur lack of training.",
        "• Machine: UI par validation na hona.",
        "• Method: Unrecorded manual adjustments.",
        "• Material: Ghalat SKU labels aur duplicate categories.",
        "Hamare Q07 features in sabhi root causes ko counteract karte hain.'"
    ], accent_color='#475569', tag="SLIDE 20")

    # Slide 21
    builder.draw_card("SLIDE 21: FMEA RISK PRIORITIZATION & RPN OPTIMIZATION", [
        "Kya bolna hai: 'Sir, Failure Mode and Effects Analysis mein RPN = Severity * Occurrence * Detection hota hai. Hamara baseline average RPN 343 tha. Automated Poka-Yoke gates lagane ke baad Occurrence aur Detection dono drop ho gaye, jisse post-control RPN 14 ho gaya—yani approx 95% risk reduction achieve hui.'",
        "Calculation: Pre-RPN 343 -> Post-RPN 14 (95.9% reduction via automated source inspection)."
    ], accent_color='#16A34A', tag="SLIDE 21")

    # Slide 22
    builder.draw_card("SLIDE 22: CLOSED-LOOP CONTINUOUS IMPROVEMENT (AUDIT-TO-FMEA)", [
        "Kya bolna hai: 'Yeh hamara key innovation loop hai: Audit logs sirf history save nahi karte; wo defect signal generate karte hain jo Pareto checklist ko update karta hai, wahan se FMEA RPN recalculate hota hai, aur validation rules refine hoti hain. This is closed-loop Kaizen.'",
        "Pipeline: Capture -> Classify -> Quantify -> Prioritize -> Improve -> Verify."
    ], accent_color='#2563EB', tag="SLIDE 22")

    # Slide 23
    builder.draw_card("SLIDE 23: DEMING’S PDCA CONTINUOUS IMPROVEMENT CYCLE", [
        "Kya bolna hai: 'Poora software development Deming ke PDCA cycle par structured hai:",
        "• Plan: Baseline defects aur CTQ targets identify kiye.",
        "• Do: Poka-Yoke aur CustomTkinter UI build kiya.",
        "• Check: 42 automated tests aur CTQ metrics verify kiye.",
        "• Act: Validation rules standardize kiye aur clean documentation freeze ki.'"
    ], accent_color='#7C3AED', tag="SLIDE 23")

    # Slide 24
    builder.draw_card("SLIDE 24: AUTOMATED QUALITY ASSURANCE & GOLDEN VIVA TAKEAWAY", [
        "Kya bolna hai: 'Sir, conclusion mein, hamara system 42 out of 42 tests passing ke sath 0.53 seconds mein verify hota hai.",
        "And to conclude with my Golden Viva statement:",
        "\"Quality Goal Q07 was achieved not merely by building a data entry screen, but by engineering a proactive Total Quality Management system: Poka-Yoke validation guarantees zero defect entry at the gate, transactional SQLite persistence guarantees atomic integrity, and automated statistical analysis transforms raw audit trails into continuous organizational learning.\" Thank you, Sir.'"
    ], accent_color='#0F172A', tag="SLIDE 24")

    # ==========================================
    # PAGES 10 TO 12: COUNTER-QUESTIONS & ANSWERS
    # ==========================================
    builder.start_new_page("TOP VIVA COUNTER-QUESTIONS")
    builder.draw_section_heading("PART 4: TOP 7 VIVA COUNTER-QUESTIONS & WINNING ANSWERS", "Critical counter-questions professors frequently ask with exact responses.")

    # Q1
    builder.draw_qa_card(1, "Yeh toh normal inventory software lag raha hai, isme TQM kahan hai?", [
        "Sir, normal software reactive hota hai—wo ghalat data accept kar leta hai aur baad mein log report check karke manually theek karte hain.",
        "Hamare system mein TQM ke 4 core pillars embedded hain:",
        "1. Poka-Yoke (Deming Principle 3): Entry gate par hi defect prevention.",
        "2. Statistical Process Control: Real-time Pareto (80/20) aur dynamic CTQ Scorecard.",
        "3. FMEA Risk Mitigation: Mathematically RPN ko 343 se 14 tak reduce karna.",
        "4. Kaizen Feedback Loop: Audit logs passive files nahi hain, wo live defect metrics ban kar FMEA ko feed karti hain."
    ], key_formula="TQM is built into the architecture, not added as a post-hoc report.")

    # Q2
    builder.draw_qa_card(2, "Agar user category mein spelling ghalat daale ya negative quantity daale toh kya hoga?", [
        "Sir, user manually category type kar hi nahi sakta kyunki humne Controlled Dropdown Taxonomy di hai.",
        "Aur agar user quantity mein negative number daalta hai, toh pehle UI validator use rokta hai, phir domain service reject karti hai, aur third line of defense mein SQLite ka CHECK(quantity >= 0) constraint database level par commit ko rollback kar deta hai.",
        "Invalid data database tak pahunch hi nahi sakta under any condition."
    ], key_formula="3-Tier Defense: UI Regex/Mask -> Python Domain Service -> SQLite Constraints.")

    # Q3
    builder.draw_qa_card(3, "Deming ka Principle 3 'Cease dependence on mass inspection' yahan kaise fit baithta hai?", [
        "Sir, mass inspection ka matlab hota hai maheene ke aakhir mein physical warehouse audit karke dhoondhna ki stock kahan ghalat hua.",
        "Deming ne kaha tha ki quality process ke andar build karo taaki inspection ki zaroorat hi na pade.",
        "Hamara Poka-Yoke validation har single entry ko gate par verify karta hai, isliye retrospective mass correction ki zaroorat khatam ho jaati hai."
    ], key_formula="Deming Principle 3 = Source inspection at the point of creation.")

    # Q4
    builder.draw_qa_card(4, "FMEA mein RPN 343 se 14 kaise hua? Formula aur calculation samjhao.", [
        "Sir, FMEA formula hai: RPN = Severity (S) * Occurrence (O) * Detection (D).",
        "• Malformed SKU ka initial score tha: S=7, O=7, D=7 => RPN = 343. Yahan detection manual checking thi isliye score high (poor) tha.",
        "• Humne automated regex check aur unique index lagaya. Isse Occurrence 7 se drop hokar 1 ho gayi, aur Detection instant ho gayi (D=1).",
        "• Naya score: 7 * 1 * 1 = 7 (overall average dropped from 343 to 14), which is a 95.9% risk reduction."
    ], key_formula="RPN = Severity x Occurrence x Detection (Target: Lowest RPN through Poka-Yoke).")

    # Q5
    builder.draw_qa_card(5, "SQLite kyun use kiya? Agar app achanak crash ho jaaye toh audit log aadha toh nahi bachega?", [
        "Sir, SQLite in-process, zero-configuration aur lightweight hai jo university desktop evaluation ke liye ideal hai.",
        "Data safety ke liye humne Write-Ahead Logging (WAL) enable kiya hai aur har operation atomic transaction (BEGIN TRANSACTION ... COMMIT) ke andar hota hai.",
        "Product update aur audit log entry dono ek hi transaction mein commit hote hain. Agar power cut ya crash hua, toh SQLite automatic rollback kar deta hai; aadha record kabhi commit nahi ho sakta."
    ], key_formula="ACID Transactions: All-or-nothing guarantee via SQLite WAL Mode.")

    # Q6
    builder.draw_qa_card(6, "Pareto chart mein 'Vital Few' ka kya relevance hai?", [
        "Sir, Juran ke 80/20 rule ke mutabiq, 80% problems sirf 20% causes ki wajah se aati hain.",
        "Hamare Pareto chart mein Missing Fields (64) aur Invalid Price Formatting (42) milkar 67.9% errors create kar rahe the.",
        "Evaluators ko yeh dikhata hai ki management ko saare 100 features par time waste karne ki jagah pehle in top 2 vital few failure modes par Poka-Yoke lagana chahiye tha, jo humne effectively kiya."
    ], key_formula="Cumulative % = (Sum Defects_1..k / Total Defects) * 100.")

    # Q7
    builder.draw_qa_card(7, "Architecture mein 'Screen Never Writes SQL' kyun zaroori hai?", [
        "Sir, agar UI screens direct SQL queries likhein, toh data validation bypass ho sakti hai aur code testable nahi rehta.",
        "Hamare 3-tier architecture mein GUI view sirf ProductService ko call karta hai, jahan business rules check hote hain, aur persistence sirf ProductRepository handle karta hai.",
        "Isi wajah se hum 42/42 pytest tests bina UI open kiye headless mode mein 0.53 seconds mein verify kar paate hain."
    ], key_formula="Separation of Concerns: Views -> Services/Validators -> Repositories -> SQLite.")

    builder.close()

if __name__ == '__main__':
    build_pdf()
