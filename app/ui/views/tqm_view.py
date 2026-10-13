"""Total Quality Management (TQM) Module View: CTQ, Checksheet, Pareto, Fishbone, FMEA, SIPOC, PDCA."""

from typing import Any, Callable, Dict, List, Optional
import customtkinter as ctk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from app.config import DEFECT_CATEGORIES, DEFECT_SEVERITIES, PDCA_STAGES
from app.models.tqm import Defect, FMEAItem, PDCARecord
from app.services import tqm_service
from app.ui.components import TableView
from app.ui.theme import THEME, FONTS
from app.utils.validators import ValidationError


class AddDefectModal(ctk.CTkToplevel):
    """Modal dialog to log a new defect observation into the TQM checksheet."""

    def __init__(self, parent, on_success: Optional[Callable[[], None]] = None):
        super().__init__(parent)
        self.on_success = on_success

        self.title("Log Defect / Checksheet Observation")
        self.geometry("500x480")
        self.resizable(False, False)
        self.configure(fg_color=THEME["card_bg"])
        self.transient(parent)
        self.grab_set()

        # Center
        self.update_idletasks()
        try:
            x = parent.winfo_x() + (parent.winfo_width() - 500) // 2
            y = parent.winfo_y() + (parent.winfo_height() - 480) // 2
            self.geometry(f"+{max(0, x)}+{max(0, y)}")
        except Exception:
            pass

        self._build_ui()

    def _build_ui(self):
        header = ctk.CTkFrame(self, fg_color=THEME["danger"], height=48, corner_radius=0)
        header.pack(fill="x")
        ctk.CTkLabel(header, text="NEW DEFECT CHECKSHEET ENTRY", font=FONTS["h3"], text_color="#FFFFFF").pack(side="left", padx=20, pady=12)

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=24, pady=16)

        self.lbl_err = ctk.CTkLabel(body, text="", font=FONTS["small_bold"], text_color=THEME["danger"], wraplength=440)

        # Category
        ctk.CTkLabel(body, text="Defect Category *", font=FONTS["small_bold"], text_color=THEME["text_body"]).pack(anchor="w")
        self.combo_cat = ctk.CTkOptionMenu(body, values=DEFECT_CATEGORIES, height=34, font=FONTS["body"], fg_color=THEME["bg_main"], button_color=THEME["secondary"], text_color=THEME["text_dark"], dropdown_text_color=THEME["text_dark"], dropdown_fg_color="#FFFFFF")
        self.combo_cat.set(DEFECT_CATEGORIES[0])
        self.combo_cat.pack(fill="x", pady=(2, 10))

        # Severity & Count
        row = ctk.CTkFrame(body, fg_color="transparent")
        row.pack(fill="x", pady=(2, 10))
        row.grid_columnconfigure((0, 1), weight=1)

        c1 = ctk.CTkFrame(row, fg_color="transparent")
        c1.grid(row=0, column=0, padx=(0, 6), sticky="ew")
        ctk.CTkLabel(c1, text="Severity Level *", font=FONTS["small_bold"], text_color=THEME["text_body"]).pack(anchor="w")
        self.combo_sev = ctk.CTkOptionMenu(c1, values=DEFECT_SEVERITIES, height=34, font=FONTS["body"], fg_color=THEME["bg_main"], button_color=THEME["secondary"], text_color=THEME["text_dark"], dropdown_text_color=THEME["text_dark"], dropdown_fg_color="#FFFFFF")
        self.combo_sev.set(DEFECT_SEVERITIES[1])
        self.combo_sev.pack(fill="x", pady=(2, 0))

        c2 = ctk.CTkFrame(row, fg_color="transparent")
        c2.grid(row=0, column=1, padx=(6, 0), sticky="ew")
        ctk.CTkLabel(c2, text="Occurrence Frequency *", font=FONTS["small_bold"], text_color=THEME["text_body"]).pack(anchor="w")
        self.entry_cnt = ctk.CTkEntry(c2, height=34, font=FONTS["body"], border_color=THEME["card_border"])
        self.entry_cnt.insert(0, "1")
        self.entry_cnt.pack(fill="x", pady=(2, 0))

        # Description
        ctk.CTkLabel(body, text="Defect Description *", font=FONTS["small_bold"], text_color=THEME["text_body"]).pack(anchor="w")
        self.entry_desc = ctk.CTkEntry(body, placeholder_text="Explain observed failure mode...", height=34, font=FONTS["body"], border_color=THEME["card_border"])
        self.entry_desc.pack(fill="x", pady=(2, 10))

        # Corrective Action
        ctk.CTkLabel(body, text="Immediate Corrective / Preventive Action", font=FONTS["small_bold"], text_color=THEME["text_body"]).pack(anchor="w")
        self.entry_action = ctk.CTkEntry(body, placeholder_text="Remediation steps...", height=34, font=FONTS["body"], border_color=THEME["card_border"])
        self.entry_action.pack(fill="x", pady=(2, 16))

        # Buttons
        b_bar = ctk.CTkFrame(self, fg_color="transparent")
        b_bar.pack(fill="x", padx=24, pady=16)

        ctk.CTkButton(b_bar, text="Cancel", font=FONTS["body"], fg_color=THEME["bg_main"], text_color=THEME["text_body"], border_width=1, border_color=THEME["card_border"], height=36, command=self.destroy).pack(side="right", padx=(8, 0))
        ctk.CTkButton(b_bar, text="Log Defect", font=FONTS["body_bold"], fg_color=THEME["danger"], hover_color="#B91C1C", text_color="#FFFFFF", height=36, command=self._save).pack(side="right")

    def _save(self):
        cat = self.combo_cat.get()
        sev = self.combo_sev.get()
        desc = self.entry_desc.get().strip()
        act = self.entry_action.get().strip()
        try:
            cnt = int(self.entry_cnt.get().strip())
            tqm_service.add_defect(
                category=cat,
                description=desc,
                severity=sev,
                occurrence_count=cnt,
                corrective_action=act,
            )
            if self.on_success:
                self.on_success()
            self.destroy()
        except ValidationError as e:
            self.lbl_err.configure(text=e.message)
            self.lbl_err.pack(fill="x", pady=(0, 8), before=self.combo_cat)
        except Exception as ex:
            self.lbl_err.configure(text=str(ex))
            self.lbl_err.pack(fill="x", pady=(0, 8), before=self.combo_cat)


class AddFMEAModal(ctk.CTkToplevel):
    """Modal to add a new FMEA line item with live RPN preview."""

    def __init__(self, parent, on_success: Optional[Callable[[], None]] = None):
        super().__init__(parent)
        self.on_success = on_success

        self.title("Add FMEA Failure Mode Entry")
        self.geometry("560x600")
        self.resizable(False, False)
        self.configure(fg_color=THEME["card_bg"])
        self.transient(parent)
        self.grab_set()

        self.update_idletasks()
        try:
            x = parent.winfo_x() + (parent.winfo_width() - 560) // 2
            y = parent.winfo_y() + (parent.winfo_height() - 600) // 2
            self.geometry(f"+{max(0, x)}+{max(0, y)}")
        except Exception:
            pass

        self._build_ui()

    def _build_ui(self):
        header = ctk.CTkFrame(self, fg_color=THEME["primary"], height=48, corner_radius=0)
        header.pack(fill="x")
        ctk.CTkLabel(header, text="FMEA RISK SCORING WORKSHEET", font=FONTS["h3"], text_color="#FFFFFF").pack(side="left", padx=20, pady=12)

        body = ctk.CTkScrollableFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=24, pady=16)

        ctk.CTkLabel(body, text="Process Step *", font=FONTS["small_bold"], text_color=THEME["text_body"]).pack(anchor="w")
        self.entry_step = ctk.CTkEntry(body, placeholder_text="e.g. Purchase Receipt Entry", height=32, font=FONTS["body"])
        self.entry_step.pack(fill="x", pady=(2, 8))

        ctk.CTkLabel(body, text="Potential Failure Mode *", font=FONTS["small_bold"], text_color=THEME["text_body"]).pack(anchor="w")
        self.entry_mode = ctk.CTkEntry(body, placeholder_text="e.g. Typo in Unit Price", height=32, font=FONTS["body"])
        self.entry_mode.pack(fill="x", pady=(2, 8))

        ctk.CTkLabel(body, text="Potential Failure Effect *", font=FONTS["small_bold"], text_color=THEME["text_body"]).pack(anchor="w")
        self.entry_effect = ctk.CTkEntry(body, placeholder_text="e.g. Inventory valuation overstatement", height=32, font=FONTS["body"])
        self.entry_effect.pack(fill="x", pady=(2, 8))

        ctk.CTkLabel(body, text="Root Cause *", font=FONTS["small_bold"], text_color=THEME["text_body"]).pack(anchor="w")
        self.entry_cause = ctk.CTkEntry(body, placeholder_text="e.g. Manual decimal omission", height=32, font=FONTS["body"])
        self.entry_cause.pack(fill="x", pady=(2, 8))

        ctk.CTkLabel(body, text="Existing Controls", font=FONTS["small_bold"], text_color=THEME["text_body"]).pack(anchor="w")
        self.entry_controls = ctk.CTkEntry(body, placeholder_text="e.g. Visual verification", height=32, font=FONTS["body"])
        self.entry_controls.pack(fill="x", pady=(2, 8))

        # Scores 3-Column
        s_row = ctk.CTkFrame(body, fg_color="transparent")
        s_row.pack(fill="x", pady=(2, 8))
        s_row.grid_columnconfigure((0, 1, 2), weight=1)

        scores_list = [str(i) for i in range(1, 11)]

        c_s = ctk.CTkFrame(s_row, fg_color="transparent")
        c_s.grid(row=0, column=0, padx=2, sticky="ew")
        ctk.CTkLabel(c_s, text="Severity (1-10)", font=FONTS["small_bold"], text_color=THEME["danger"]).pack(anchor="w")
        self.combo_sev = ctk.CTkOptionMenu(c_s, values=scores_list, height=32, command=self._update_rpn, fg_color=THEME["bg_main"], button_color=THEME["secondary"], text_color=THEME["text_dark"], dropdown_text_color=THEME["text_dark"], dropdown_fg_color="#FFFFFF")
        self.combo_sev.set("7")
        self.combo_sev.pack(fill="x", pady=(2, 0))

        c_o = ctk.CTkFrame(s_row, fg_color="transparent")
        c_o.grid(row=0, column=1, padx=2, sticky="ew")
        ctk.CTkLabel(c_o, text="Occurrence (1-10)", font=FONTS["small_bold"], text_color=THEME["warning"]).pack(anchor="w")
        self.combo_occ = ctk.CTkOptionMenu(c_o, values=scores_list, height=32, command=self._update_rpn, fg_color=THEME["bg_main"], button_color=THEME["secondary"], text_color=THEME["text_dark"], dropdown_text_color=THEME["text_dark"], dropdown_fg_color="#FFFFFF")
        self.combo_occ.set("5")
        self.combo_occ.pack(fill="x", pady=(2, 0))

        c_d = ctk.CTkFrame(s_row, fg_color="transparent")
        c_d.grid(row=0, column=2, padx=2, sticky="ew")
        ctk.CTkLabel(c_d, text="Detection (1-10)", font=FONTS["small_bold"], text_color=THEME["info"]).pack(anchor="w")
        self.combo_det = ctk.CTkOptionMenu(c_d, values=scores_list, height=32, command=self._update_rpn, fg_color=THEME["bg_main"], button_color=THEME["secondary"], text_color=THEME["text_dark"], dropdown_text_color=THEME["text_dark"], dropdown_fg_color="#FFFFFF")
        self.combo_det.set("5")
        self.combo_det.pack(fill="x", pady=(2, 0))

        # RPN Preview Card
        self.rpn_box = ctk.CTkFrame(body, fg_color=THEME["bg_main"], corner_radius=6, border_width=1, border_color=THEME["card_border"])
        self.rpn_box.pack(fill="x", pady=(4, 10))

        self.lbl_rpn = ctk.CTkLabel(
            self.rpn_box,
            text="RPN = 7 × 5 × 5 = 175 (Medium Risk)",
            font=FONTS["body_bold"],
            text_color=THEME["primary"],
        )
        self.lbl_rpn.pack(padx=12, pady=6)

        ctk.CTkLabel(body, text="Recommended Action *", font=FONTS["small_bold"], text_color=THEME["text_body"]).pack(anchor="w")
        self.entry_rec = ctk.CTkEntry(body, placeholder_text="e.g. Implement input masking and numeric range checks", height=32, font=FONTS["body"])
        self.entry_rec.pack(fill="x", pady=(2, 8))

        ctk.CTkLabel(body, text="Action Owner *", font=FONTS["small_bold"], text_color=THEME["text_body"]).pack(anchor="w")
        self.entry_owner = ctk.CTkEntry(body, placeholder_text="e.g. Dheeraj Khetwal", height=32, font=FONTS["body"])
        self.entry_owner.insert(0, "Dheeraj Khetwal")
        self.entry_owner.pack(fill="x", pady=(2, 12))

        # Bottom
        b_bar = ctk.CTkFrame(self, fg_color="transparent")
        b_bar.pack(fill="x", padx=24, pady=16)
        ctk.CTkButton(b_bar, text="Cancel", font=FONTS["body"], fg_color=THEME["bg_main"], text_color=THEME["text_body"], border_width=1, border_color=THEME["card_border"], height=36, command=self.destroy).pack(side="right", padx=(8, 0))
        ctk.CTkButton(b_bar, text="Add FMEA Item", font=FONTS["body_bold"], fg_color=THEME["primary"], hover_color=THEME["primary_hover"], height=36, command=self._save).pack(side="right")

    def _update_rpn(self, _=None):
        s = int(self.combo_sev.get())
        o = int(self.combo_occ.get())
        d = int(self.combo_det.get())
        rpn = s * o * d
        risk = "High Risk" if rpn >= 200 else ("Medium Risk" if rpn >= 100 else "Low Risk")
        self.lbl_rpn.configure(text=f"RPN = {s} × {o} × {d} = {rpn} ({risk})")

    def _save(self):
        step = self.entry_step.get().strip()
        mode = self.entry_mode.get().strip()
        eff = self.entry_effect.get().strip()
        cause = self.entry_cause.get().strip()
        ctrl = self.entry_controls.get().strip() or "None"
        s = int(self.combo_sev.get())
        o = int(self.combo_occ.get())
        d = int(self.combo_det.get())
        rec = self.entry_rec.get().strip()
        owner = self.entry_owner.get().strip()

        if not (step and mode and eff and cause and rec and owner):
            return

        tqm_service.add_fmea_item(
            process_step=step,
            failure_mode=mode,
            failure_effect=eff,
            potential_cause=cause,
            existing_controls=ctrl,
            severity=s,
            occurrence=o,
            detection=d,
            recommended_action=rec,
            owner=owner,
        )
        if self.on_success:
            self.on_success()
        self.destroy()


class TQMView(ctk.CTkFrame):
    """TQM Quality Control & Continuous Improvement Dashboard."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self.pareto_canvas_widget = None

        self._build_ui()
        self.refresh()

    def _build_ui(self):
        # 1. Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 16))

        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left")

        lbl_title = ctk.CTkLabel(
            title_box,
            text="TQM Quality & Analytics Suite",
            font=FONTS["h1"],
            text_color=THEME["text_dark"],
        )
        lbl_title.pack(anchor="w")

        lbl_sub = ctk.CTkLabel(
            title_box,
            text="BBAT104 Course Project: CTQ • Checksheets • Pareto (80/20) • Fishbone • FMEA • SIPOC • PDCA",
            font=FONTS["small"],
            text_color=THEME["text_muted"],
        )
        lbl_sub.pack(anchor="w")

        btn_refresh = ctk.CTkButton(
            header,
            text="Recalculate Quality Metrics",
            font=FONTS["body"],
            fg_color=THEME["card_bg"],
            text_color=THEME["text_body"],
            border_width=1,
            border_color=THEME["card_border"],
            hover_color=THEME["table_header_bg"],
            height=36,
            command=self.refresh,
        )
        btn_refresh.pack(side="right")

        # 2. Main Tabview
        self.tabview = ctk.CTkTabview(
            self,
            fg_color=THEME["card_bg"],
            segmented_button_selected_color=THEME["primary"],
            segmented_button_selected_hover_color=THEME["primary_hover"],
            corner_radius=THEME["card_radius"],
        )
        self.tabview.pack(fill="both", expand=True)

        self.tab_ctq = self.tabview.add("1. CTQ Scorecard")
        self.tab_pareto = self.tabview.add("2. Pareto Analysis (80/20)")
        self.tab_fishbone = self.tabview.add("3. Fishbone (Ishikawa)")
        self.tab_fmea = self.tabview.add("4. FMEA Risk Matrix")
        self.tab_sipoc = self.tabview.add("5. SIPOC Process Map")
        self.tab_pdca = self.tabview.add("6. PDCA Tracker")

        self._build_ctq_tab()
        self._build_pareto_tab()
        self._build_fishbone_tab()
        self._build_fmea_tab()
        self._build_sipoc_tab()
        self._build_pdca_tab()

    # -------------------------------------------------------------------------
    # TAB 1: CTQ SCORECARD
    # -------------------------------------------------------------------------
    def _build_ctq_tab(self):
        lbl = ctk.CTkLabel(
            self.tab_ctq,
            text="CRITICAL TO QUALITY (CTQ) CHARACTERISTICS & LIVE COMPLIANCE SCORECARD",
            font=FONTS["h3"],
            text_color=THEME["text_muted"],
        )
        lbl.pack(anchor="w", padx=16, pady=(12, 6))

        cols = [
            {"key": "ctq_id", "title": "CTQ ID", "width": 80, "align": "center"},
            {"key": "characteristic", "title": "Quality Characteristic", "width": 200, "align": "w"},
            {"key": "operational_definition", "title": "Operational Definition", "width": 340, "align": "w"},
            {"key": "target", "title": "Goal Target", "width": 90, "align": "center"},
            {"key": "actual", "title": "Actual Measured", "width": 110, "align": "center"},
            {"key": "defect_count", "title": "Defects", "width": 70, "align": "center"},
            {"key": "status", "title": "Result", "width": 80, "align": "center"},
        ]
        self.table_ctq = TableView(self.tab_ctq, columns=cols)
        self.table_ctq.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    # -------------------------------------------------------------------------
    # TAB 2: PARETO ANALYSIS & DEFECT CHECKSHEET
    # -------------------------------------------------------------------------
    def _build_pareto_tab(self):
        # 2 Columns: Chart on Left (60%), Defect Checksheet on Right (40%)
        container = ctk.CTkFrame(self.tab_pareto, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=8, pady=8)
        container.grid_columnconfigure(0, weight=3)
        container.grid_columnconfigure(1, weight=2)
        container.grid_rowconfigure(0, weight=1)

        # Left: Matplotlib Chart Card
        left_card = ctk.CTkFrame(container, fg_color=THEME["bg_main"], corner_radius=6, border_width=1, border_color=THEME["card_border"])
        left_card.grid(row=0, column=0, padx=(0, 6), sticky="nsew")

        p_head = ctk.CTkFrame(left_card, fg_color="transparent")
        p_head.pack(fill="x", padx=12, pady=(10, 4))

        ctk.CTkLabel(p_head, text="DEFECT FREQUENCY PARETO CHART (80/20 RULE)", font=FONTS["h3"], text_color=THEME["text_muted"]).pack(side="left")

        self.pareto_container = ctk.CTkFrame(left_card, fg_color="transparent")
        self.pareto_container.pack(fill="both", expand=True, padx=6, pady=(0, 6))

        self.lbl_vital_few = ctk.CTkLabel(
            left_card,
            text="Vital Few Categories: Calculating...",
            font=FONTS["small_bold"],
            text_color=THEME["primary"],
        )
        self.lbl_vital_few.pack(fill="x", padx=12, pady=(0, 8))

        # Right: Defect Checksheet Table Card
        right_card = ctk.CTkFrame(container, fg_color=THEME["bg_main"], corner_radius=6, border_width=1, border_color=THEME["card_border"])
        right_card.grid(row=0, column=1, padx=(6, 0), sticky="nsew")

        r_head = ctk.CTkFrame(right_card, fg_color="transparent")
        r_head.pack(fill="x", padx=12, pady=(10, 4))
        ctk.CTkLabel(r_head, text="DEFECT CHECKSHEET LOG", font=FONTS["h3"], text_color=THEME["text_muted"]).pack(side="left")

        ctk.CTkButton(
            r_head,
            text="+ Log Defect",
            font=FONTS["small_bold"],
            fg_color=THEME["danger"],
            hover_color="#B91C1C",
            width=90,
            height=28,
            command=lambda: AddDefectModal(self, on_success=self.refresh),
        ).pack(side="right")

        cols = [
            {"key": "defect_code", "title": "Code", "width": 75, "align": "center"},
            {"key": "category", "title": "Category", "width": 110, "align": "w"},
            {"key": "severity", "title": "Sev", "width": 60, "align": "center"},
            {"key": "occurrence_count", "title": "Qty", "width": 45, "align": "center"},
            {"key": "status", "title": "Status", "width": 65, "align": "center"},
        ]
        self.table_defects = TableView(right_card, columns=cols)
        self.table_defects.pack(fill="both", expand=True, padx=8, pady=(0, 8))

    # -------------------------------------------------------------------------
    # TAB 3: FISHBONE (ISHIKAWA) ANALYSIS
    # -------------------------------------------------------------------------
    def _build_fishbone_tab(self):
        lbl = ctk.CTkLabel(
            self.tab_fishbone,
            text="ISHIKAWA CAUSE-AND-EFFECT (FISHBONE) DIAGRAM: INVENTORY DATA INACCURACY (Q07)",
            font=FONTS["h3"],
            text_color=THEME["text_muted"],
        )
        lbl.pack(anchor="w", padx=16, pady=(12, 8))

        # 4 Quadrants layout
        quad_frame = ctk.CTkFrame(self.tab_fishbone, fg_color="transparent")
        quad_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        quad_frame.grid_columnconfigure((0, 1), weight=1)
        quad_frame.grid_rowconfigure((0, 1), weight=1)

        fish_data = tqm_service.get_fishbone_data()["categories"]
        cat_colors = {
            "People": THEME["primary"],
            "Process": THEME["warning"],
            "Software Code": THEME["danger"],
            "Infrastructure": THEME["info"],
        }

        positions = [
            ("People", 0, 0),
            ("Process", 0, 1),
            ("Software Code", 1, 0),
            ("Infrastructure", 1, 1),
        ]

        for cat_name, r, c in positions:
            card = ctk.CTkFrame(quad_frame, fg_color=THEME["bg_main"], corner_radius=6, border_width=1, border_color=THEME["card_border"])
            card.grid(row=r, column=c, padx=6, pady=6, sticky="nsew")

            accent = ctk.CTkFrame(card, fg_color=cat_colors[cat_name], height=4)
            accent.pack(fill="x", padx=8, pady=(6, 4))

            lbl_c = ctk.CTkLabel(card, text=f"CATEGORY: {cat_name.upper()}", font=FONTS["body_bold"], text_color=cat_colors[cat_name], anchor="w")
            lbl_c.pack(fill="x", padx=12, pady=(2, 6))

            for item in fish_data.get(cat_name, []):
                i_row = ctk.CTkFrame(card, fg_color="transparent")
                i_row.pack(fill="x", padx=12, pady=2)
                ctk.CTkLabel(i_row, text="•", font=FONTS["body_bold"], text_color=cat_colors[cat_name], width=16).pack(side="left")
                ctk.CTkLabel(i_row, text=item, font=FONTS["small"], text_color=THEME["text_body"], wraplength=420, justify="left").pack(side="left", fill="x", expand=True)

    # -------------------------------------------------------------------------
    # TAB 4: FMEA RISK WORKSHEET
    # -------------------------------------------------------------------------
    def _build_fmea_tab(self):
        f_top = ctk.CTkFrame(self.tab_fmea, fg_color="transparent")
        f_top.pack(fill="x", padx=16, pady=(12, 6))

        ctk.CTkLabel(
            f_top,
            text="FAILURE MODE AND EFFECTS ANALYSIS (FMEA) • FORMULA: RPN = SEVERITY × OCCURRENCE × DETECTION",
            font=FONTS["h3"],
            text_color=THEME["text_muted"],
        ).pack(side="left")

        ctk.CTkButton(
            f_top,
            text="+ Add FMEA Item",
            font=FONTS["small_bold"],
            fg_color=THEME["primary"],
            hover_color=THEME["primary_hover"],
            height=30,
            command=lambda: AddFMEAModal(self, on_success=self.refresh),
        ).pack(side="right")

        cols = [
            {"key": "process_step", "title": "Process Step", "width": 140, "align": "w"},
            {"key": "failure_mode", "title": "Failure Mode", "width": 170, "align": "w"},
            {"key": "failure_effect", "title": "Failure Effect", "width": 200, "align": "w"},
            {"key": "severity", "title": "S (1-10)", "width": 65, "align": "center"},
            {"key": "occurrence", "title": "O (1-10)", "width": 65, "align": "center"},
            {"key": "detection", "title": "D (1-10)", "width": 65, "align": "center"},
            {"key": "rpn", "title": "RPN Score", "width": 75, "align": "center"},
            {"key": "risk_level", "title": "Risk Class", "width": 85, "align": "center"},
            {"key": "recommended_action", "title": "Recommended Action", "width": 220, "align": "w"},
            {"key": "owner", "title": "Owner", "width": 110, "align": "w"},
        ]
        self.table_fmea = TableView(self.tab_fmea, columns=cols)
        self.table_fmea.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    # -------------------------------------------------------------------------
    # TAB 5: SIPOC PROCESS MAP
    # -------------------------------------------------------------------------
    def _build_sipoc_tab(self):
        lbl = ctk.CTkLabel(
            self.tab_sipoc,
            text="SIPOC PROCESS FLOW MAP: SUPPLIERS → INPUTS → PROCESS → OUTPUTS → CUSTOMERS",
            font=FONTS["h3"],
            text_color=THEME["text_muted"],
        )
        lbl.pack(anchor="w", padx=16, pady=(12, 6))

        cols = [
            {"key": "suppliers", "title": "Suppliers", "width": 170, "align": "w"},
            {"key": "inputs", "title": "Inputs", "width": 200, "align": "w"},
            {"key": "process", "title": "Process Steps", "width": 250, "align": "w"},
            {"key": "outputs", "title": "Outputs", "width": 220, "align": "w"},
            {"key": "customers", "title": "Customers", "width": 180, "align": "w"},
        ]
        self.table_sipoc = TableView(self.tab_sipoc, columns=cols)
        self.table_sipoc.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    # -------------------------------------------------------------------------
    # TAB 6: PDCA IMPROVEMENT TRACKER
    # -------------------------------------------------------------------------
    def _build_pdca_tab(self):
        lbl = ctk.CTkLabel(
            self.tab_pdca,
            text="CONTINUOUS IMPROVEMENT TRACKER (PLAN - DO - CHECK - ACT)",
            font=FONTS["h3"],
            text_color=THEME["text_muted"],
        )
        lbl.pack(anchor="w", padx=16, pady=(12, 6))

        cols = [
            {"key": "title", "title": "Initiative Title", "width": 240, "align": "w"},
            {"key": "stage", "title": "Stage", "width": 70, "align": "center"},
            {"key": "problem_statement", "title": "Problem Statement", "width": 260, "align": "w"},
            {"key": "plan_description", "title": "Plan / Action Taken", "width": 260, "align": "w"},
            {"key": "expected_result", "title": "Expected Result", "width": 200, "align": "w"},
            {"key": "owner", "title": "Owner", "width": 110, "align": "w"},
            {"key": "status", "title": "Status", "width": 90, "align": "center"},
        ]
        self.table_pdca = TableView(self.tab_pdca, columns=cols)
        self.table_pdca.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    # -------------------------------------------------------------------------
    # REFRESH & RENDER
    # -------------------------------------------------------------------------
    def refresh(self):
        # 1. CTQ Scorecard
        ctq_data = tqm_service.calculate_ctq_metrics()
        self.table_ctq.set_data(ctq_data["metrics"])

        # 2. Defect Checksheets
        defects = tqm_service.get_all_defects()
        d_rows = [d.to_dict() for d in defects]
        self.table_defects.set_data(d_rows)

        # 3. Pareto Chart
        self._render_pareto_chart()

        # 4. FMEA Items
        fmea_items = tqm_service.get_all_fmea()
        f_rows = [f.to_dict() for f in fmea_items]
        self.table_fmea.set_data(f_rows)

        # 5. SIPOC
        sipoc_stages = tqm_service.get_sipoc_data()["stages"]
        self.table_sipoc.set_data(sipoc_stages)

        # 6. PDCA
        pdca_items = tqm_service.get_all_pdca()
        p_rows = [p.to_dict() for p in pdca_items]
        self.table_pdca.set_data(p_rows)

    def _render_pareto_chart(self):
        if self.pareto_canvas_widget:
            self.pareto_canvas_widget.destroy()

        pareto_data = tqm_service.calculate_pareto_data()

        fig = Figure(figsize=(5.5, 3.8), dpi=100)
        fig.patch.set_facecolor("#F8FAFC")
        ax1 = fig.add_subplot(111)
        ax1.set_facecolor("#FFFFFF")

        if pareto_data["categories"]:
            cats = pareto_data["categories"]
            counts = pareto_data["counts"]
            cum_pcts = pareto_data["cumulative_percentages"]

            # Bar plot on primary y-axis
            bars = ax1.bar(cats, counts, color="#2563EB", width=0.55, alpha=0.9, label="Defect Count")
            ax1.set_ylabel("Defect Frequency (Count)", color="#2563EB", fontsize=9, fontweight="bold")
            ax1.tick_params(axis="y", labelcolor="#2563EB", labelsize=8)
            ax1.tick_params(axis="x", labelrotation=25, labelsize=8, colors="#334155")
            ax1.set_ylim(0, max(counts) * 1.25 if counts else 10)

            # Cumulative % on secondary y-axis
            ax2 = ax1.twinx()
            ax2.plot(cats, cum_pcts, color="#DC2626", marker="o", linewidth=2.0, markersize=5, label="Cumulative %")
            ax2.set_ylabel("Cumulative Percentage (%)", color="#DC2626", fontsize=9, fontweight="bold")
            ax2.tick_params(axis="y", labelcolor="#DC2626", labelsize=8)
            ax2.set_ylim(0, 110)

            # 80% Cutoff Reference Line
            ax2.axhline(80, color="#16A34A", linestyle="--", linewidth=1.5, alpha=0.8, label="80% Cutoff Line")
            ax2.text(
                len(cats) - 1,
                82,
                "80% Threshold",
                color="#16A34A",
                fontsize=8,
                fontweight="bold",
                ha="right",
            )

            # Annotate bar counts
            for bar in bars:
                h = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width() / 2, h + 0.3, f"{int(h)}", ha="center", va="bottom", fontsize=8, color="#0F172A", fontweight="bold")

            vital_str = ", ".join(pareto_data["vital_few"])
            self.lbl_vital_few.configure(
                text=f"Total Defects Recorded: {pareto_data['total_defects']} • Vital Few (80% Root Causes): {vital_str}"
            )
        else:
            ax1.text(0.5, 0.5, "No Defect Data Available for Pareto Chart", ha="center", va="center", color="#94A3B8")
            ax1.axis("off")
            self.lbl_vital_few.configure(text="No recorded defects in database.")

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.pareto_container)
        canvas.draw()
        self.pareto_canvas_widget = canvas.get_tk_widget()
        self.pareto_canvas_widget.pack(fill="both", expand=True)
