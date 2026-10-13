"""Modern scrollable table view component for CustomTkinter."""

from typing import Any, Callable, Dict, List, Optional
import customtkinter as ctk
from app.ui.theme import THEME, FONTS


class TableView(ctk.CTkFrame):
    """Custom scrollable table with alternating rows, custom columns, and action buttons."""

    def __init__(
        self,
        master,
        columns: List[Dict[str, Any]],  # e.g. [{"key": "sku", "title": "SKU", "width": 120, "align": "w"}]
        on_select: Optional[Callable[[Dict[str, Any]], None]] = None,
        empty_text: str = "No records found matching criteria.",
        **kwargs,
    ):
        super().__init__(
            master,
            fg_color=THEME["card_bg"],
            corner_radius=THEME["card_radius"],
            border_width=THEME["border_width"],
            border_color=THEME["card_border"],
            **kwargs,
        )

        self.columns = columns
        self.on_select = on_select
        self.empty_text = empty_text
        self.data_rows: List[Dict[str, Any]] = []

        # 1. Header Frame
        self.header_frame = ctk.CTkFrame(
            self,
            fg_color=THEME["table_header_bg"],
            corner_radius=6,
            height=38,
        )
        self.header_frame.pack(fill="x", padx=4, pady=(4, 2))

        for col in self.columns:
            w = col.get("width", 100)
            align = col.get("align", "w")
            lbl = ctk.CTkLabel(
                self.header_frame,
                text=col["title"].upper(),
                font=FONTS["small_bold"],
                text_color=THEME["text_muted"],
                width=w,
                anchor=align,
            )
            lbl.pack(side="left", padx=6, pady=6)

        # 2. Scrollable Body Frame
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=THEME["card_border"],
            scrollbar_button_hover_color=THEME["secondary"],
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=4, pady=(0, 4))

    def set_data(
        self,
        rows: List[Dict[str, Any]],
        action_callback: Optional[Callable[[str, Dict[str, Any]], None]] = None,
        action_buttons: Optional[List[Dict[str, str]]] = None,
    ) -> None:
        """Populates table with rows and optional per-row action buttons."""
        self.data_rows = rows

        # Clear existing rows
        for child in self.scroll_frame.winfo_children():
            child.destroy()

        if not rows:
            # Empty state
            empty_lbl = ctk.CTkLabel(
                self.scroll_frame,
                text=self.empty_text,
                font=FONTS["body"],
                text_color=THEME["text_muted"],
            )
            empty_lbl.pack(fill="both", expand=True, pady=40)
            return

        for idx, row_data in enumerate(rows):
            # Alternating row colors
            row_bg = THEME["card_bg"] if idx % 2 == 0 else THEME["table_row_alt"]

            row_frame = ctk.CTkFrame(
                self.scroll_frame,
                fg_color=row_bg,
                corner_radius=4,
                height=36,
            )
            row_frame.pack(fill="x", pady=1)

            # Render standard columns
            for col in self.columns:
                key = col["key"]
                w = col.get("width", 100)
                align = col.get("align", "w")
                val_text = str(row_data.get(key, ""))

                # Status color highlight if applicable
                txt_color = THEME["text_dark"]
                if key in ("status", "risk_level"):
                    if str(val_text).lower() in ("pass", "resolved", "low risk"):
                        txt_color = THEME["success"]
                    elif str(val_text).lower() in ("warning", "under review", "medium risk", "in progress"):
                        txt_color = THEME["warning"]
                    elif str(val_text).lower() in ("fail", "critical", "high risk", "open"):
                        txt_color = THEME["danger"]

                lbl = ctk.CTkLabel(
                    row_frame,
                    text=val_text,
                    font=FONTS["small"],
                    text_color=txt_color,
                    width=w,
                    anchor=align,
                )
                lbl.pack(side="left", padx=6, pady=4)

            # Render action buttons if defined
            if action_buttons and action_callback:
                actions_box = ctk.CTkFrame(row_frame, fg_color="transparent")
                actions_box.pack(side="right", padx=6)

                for act in action_buttons:
                    act_name = act["name"]
                    btn_text = act["label"]
                    btn_color = act.get("color", THEME["primary"])

                    btn = ctk.CTkButton(
                        actions_box,
                        text=btn_text,
                        font=FONTS["small_bold"],
                        fg_color=btn_color,
                        text_color="#FFFFFF",
                        width=act.get("width", 54),
                        height=24,
                        corner_radius=4,
                        command=lambda a=act_name, r=row_data: action_callback(a, r),
                    )
                    btn.pack(side="left", padx=2)
