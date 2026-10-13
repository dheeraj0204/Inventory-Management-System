"""Audit History View (Q07 Feature 5: Immutable Audit Logging & JSON Diff Inspector)."""

import json
from typing import Any, Dict, List, Optional
import customtkinter as ctk

from app.models.audit_log import AuditLog
from app.services import audit_service
from app.ui.components import TableView
from app.ui.theme import THEME, FONTS


class AuditDetailsModal(ctk.CTkToplevel):
    """Modal inspector displaying full JSON diffs between previous and new values."""

    def __init__(self, parent, log: AuditLog):
        super().__init__(parent)

        self.log = log
        self.title(f"Audit Event Details — Log #{log.id} ({log.action})")
        self.geometry("640x560")
        self.resizable(False, False)
        self.configure(fg_color=THEME["card_bg"])

        self.transient(parent)
        self.grab_set()

        # Center on parent
        self.update_idletasks()
        try:
            x = parent.winfo_x() + (parent.winfo_width() - 640) // 2
            y = parent.winfo_y() + (parent.winfo_height() - 560) // 2
            self.geometry(f"+{max(0, x)}+{max(0, y)}")
        except Exception:
            pass

        self._build_ui()

    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color=THEME["sidebar_bg"], height=48, corner_radius=0)
        header.pack(fill="x")

        lbl_head = ctk.CTkLabel(
            header,
            text=f"AUDIT EVENT #{self.log.id}: {self.log.action} ({self.log.entity_id})",
            font=FONTS["h3"],
            text_color="#FFFFFF",
        )
        lbl_head.pack(side="left", padx=20, pady=12)

        # Meta row
        meta_box = ctk.CTkFrame(self, fg_color=THEME["bg_main"], corner_radius=6, border_width=1, border_color=THEME["card_border"])
        meta_box.pack(fill="x", padx=20, pady=(16, 12))

        r1 = ctk.CTkFrame(meta_box, fg_color="transparent")
        r1.pack(fill="x", padx=12, pady=6)

        ctk.CTkLabel(r1, text=f"Timestamp (UTC): {self.log.timestamp}", font=FONTS["small_bold"], text_color=THEME["text_muted"]).pack(side="left")
        ctk.CTkLabel(r1, text=f"Entity: {self.log.entity_type} • ID: {self.log.entity_id}", font=FONTS["small_bold"], text_color=THEME["primary"]).pack(side="right")

        r2 = ctk.CTkFrame(meta_box, fg_color="transparent")
        r2.pack(fill="x", padx=12, pady=(0, 6))
        ctk.CTkLabel(r2, text=f"Change Reason: {self.log.reason or 'None specified'}", font=FONTS["small"], text_color=THEME["text_dark"]).pack(side="left")

        # JSON Diff Panels (Side by side)
        diff_frame = ctk.CTkFrame(self, fg_color="transparent")
        diff_frame.pack(fill="both", expand=True, padx=20, pady=(0, 16))
        diff_frame.grid_columnconfigure((0, 1), weight=1)
        diff_frame.grid_rowconfigure(0, weight=1)

        # Left: Previous Values (JSON)
        box_old = ctk.CTkFrame(diff_frame, fg_color=THEME["card_bg"], corner_radius=6, border_width=1, border_color=THEME["card_border"])
        box_old.grid(row=0, column=0, padx=(0, 6), sticky="nsew")

        lbl_o_title = ctk.CTkLabel(box_old, text="PREVIOUS VALUES (OLD)", font=FONTS["small_bold"], text_color=THEME["danger"])
        lbl_o_title.pack(fill="x", padx=10, pady=(8, 4))

        txt_old = ctk.CTkTextbox(box_old, font=FONTS["code"], fg_color=THEME["bg_main"], text_color=THEME["text_body"])
        txt_old.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        old_formatted = json.dumps(self.log.get_old_dict(), indent=2) if self.log.old_values else "No previous record (Initial Create)"
        txt_old.insert("1.0", old_formatted)
        txt_old.configure(state="disabled")

        # Right: New Values (JSON)
        box_new = ctk.CTkFrame(diff_frame, fg_color=THEME["card_bg"], corner_radius=6, border_width=1, border_color=THEME["card_border"])
        box_new.grid(row=0, column=1, padx=(6, 0), sticky="nsew")

        lbl_n_title = ctk.CTkLabel(box_new, text="APPLIED VALUES (NEW)", font=FONTS["small_bold"], text_color=THEME["success"])
        lbl_n_title.pack(fill="x", padx=10, pady=(8, 4))

        txt_new = ctk.CTkTextbox(box_new, font=FONTS["code"], fg_color=THEME["bg_main"], text_color=THEME["text_body"])
        txt_new.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        new_formatted = json.dumps(self.log.get_new_dict(), indent=2) if self.log.new_values else "Record deleted (Void)"
        txt_new.insert("1.0", new_formatted)
        txt_new.configure(state="disabled")

        # Close button
        btn_close = ctk.CTkButton(
            self,
            text="Close Inspector",
            font=FONTS["body_bold"],
            fg_color=THEME["bg_main"],
            text_color=THEME["text_body"],
            border_width=1,
            border_color=THEME["card_border"],
            hover_color=THEME["table_header_bg"],
            height=36,
            command=self.destroy,
        )
        btn_close.pack(side="right", padx=20, pady=(0, 16))


class AuditView(ctk.CTkFrame):
    """Immutable audit trail screen with searching, action filtering, and JSON inspector."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

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
            text="Transactional Audit Trail (Q07 Feature 5)",
            font=FONTS["h1"],
            text_color=THEME["text_dark"],
        )
        lbl_title.pack(anchor="w")

        lbl_sub = ctk.CTkLabel(
            title_box,
            text="Tamper-proof SQLite audit logging • Structured JSON diffs • Read-only enforcement",
            font=FONTS["small"],
            text_color=THEME["text_muted"],
        )
        lbl_sub.pack(anchor="w")

        btn_refresh = ctk.CTkButton(
            header,
            text="Refresh Audit Log",
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

        # 2. Filter Toolbar
        toolbar = ctk.CTkFrame(
            self,
            fg_color=THEME["card_bg"],
            corner_radius=THEME["card_radius"],
            border_width=THEME["border_width"],
            border_color=THEME["card_border"],
            height=54,
        )
        toolbar.pack(fill="x", pady=(0, 12))

        # Search Entry
        lbl_s = ctk.CTkLabel(toolbar, text="Search Audit:", font=FONTS["small_bold"], text_color=THEME["text_muted"])
        lbl_s.pack(side="left", padx=(14, 6))

        self.entry_search = ctk.CTkEntry(
            toolbar,
            placeholder_text="Filter by product ID, reason...",
            width=260,
            height=34,
            font=FONTS["body"],
            border_color=THEME["card_border"],
        )
        self.entry_search.pack(side="left", padx=(0, 12), pady=9)
        self.entry_search.bind("<Return>", lambda _: self.refresh())

        # Action Filter Dropdown
        lbl_a = ctk.CTkLabel(toolbar, text="Action Filter:", font=FONTS["small_bold"], text_color=THEME["text_muted"])
        lbl_a.pack(side="left", padx=(6, 6))

        action_options = ["All", "CREATE", "UPDATE", "DELETE", "STOCK_ADJUSTMENT"]
        self.combo_action = ctk.CTkOptionMenu(
            toolbar,
            values=action_options,
            font=FONTS["body"],
            fg_color=THEME["bg_main"],
            button_color=THEME["secondary"],
            button_hover_color=THEME["secondary_hover"],
            text_color=THEME["text_dark"],
            dropdown_text_color=THEME["text_dark"],
            dropdown_fg_color="#FFFFFF",
            width=160,
            command=lambda _: self.refresh(),
        )
        self.combo_action.set("All")
        self.combo_action.pack(side="left", padx=(0, 12), pady=9)

        btn_find = ctk.CTkButton(
            toolbar,
            text="Filter",
            font=FONTS["small_bold"],
            fg_color=THEME["primary"],
            hover_color=THEME["primary_hover"],
            width=80,
            height=32,
            command=self.refresh,
        )
        btn_find.pack(side="left", padx=(0, 8), pady=9)

        self.lbl_count = ctk.CTkLabel(
            toolbar,
            text="0 events",
            font=FONTS["small"],
            text_color=THEME["text_muted"],
        )
        self.lbl_count.pack(side="right", padx=16)

        # 3. Audit Table
        cols = [
            {"key": "id", "title": "Log #", "width": 60, "align": "center"},
            {"key": "timestamp", "title": "Timestamp (UTC)", "width": 140, "align": "w"},
            {"key": "entity_id", "title": "Product ID", "width": 90, "align": "w"},
            {"key": "action", "title": "Action", "width": 120, "align": "center"},
            {"key": "reason", "title": "Reason / Documentation", "width": 300, "align": "w"},
        ]

        self.table = TableView(
            self,
            columns=cols,
            empty_text="No audit events found matching filters.",
        )
        self.table.pack(fill="both", expand=True)

    def refresh(self):
        search_q = self.entry_search.get().strip()
        act_filt = self.combo_action.get()

        logs = audit_service.get_audit_logs(
            search_query=search_q,
            action_filter=act_filt,
            limit=150,
        )

        rows = []
        for l in logs:
            rows.append({
                "id": str(l.id),
                "timestamp": l.timestamp,
                "entity_id": l.entity_id,
                "action": l.action,
                "reason": l.reason or "--",
                "_raw": l,
            })

        action_buttons = [
            {"name": "inspect", "label": "Inspect JSON", "color": THEME["primary"], "width": 84},
        ]

        self.table.set_data(
            rows=rows,
            action_callback=self._handle_inspect,
            action_buttons=action_buttons,
        )

        self.lbl_count.configure(text=f"Total: {len(rows)} events")

    def _handle_inspect(self, action: str, row: Dict[str, Any]):
        if action == "inspect":
            log: AuditLog = row["_raw"]
            AuditDetailsModal(self, log=log)
