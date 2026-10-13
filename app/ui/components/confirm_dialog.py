"""CustomTkinter confirmation modal dialog (Q07 Feature 4: Confirmation Modals)."""

from typing import Dict, Optional
import customtkinter as ctk
from app.ui.theme import THEME, FONTS


class ConfirmDialog(ctk.CTkToplevel):
    """Modal confirmation dialog for destructive or critical state modifications."""

    def __init__(
        self,
        parent,
        title: str,
        message: str,
        details: Optional[Dict[str, str]] = None,
        confirm_text: str = "Confirm Action",
        cancel_text: str = "Cancel",
        is_destructive: bool = False,
    ):
        super().__init__(parent)

        self.confirmed = False
        self.title(title)
        self.geometry("480x360")
        self.resizable(False, False)
        self.configure(fg_color=THEME["card_bg"])

        # Make it modal
        self.transient(parent)
        self.grab_set()

        # Center on parent window
        self.update_idletasks()
        try:
            x = parent.winfo_x() + (parent.winfo_width() - 480) // 2
            y = parent.winfo_y() + (parent.winfo_height() - 360) // 2
            self.geometry(f"+{max(0, x)}+{max(0, y)}")
        except Exception:
            pass

        # Top Accent Banner
        banner_color = THEME["danger"] if is_destructive else THEME["warning"]
        self.banner = ctk.CTkFrame(self, fg_color=banner_color, height=6, corner_radius=0)
        self.banner.pack(fill="x")

        # Main Content
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=24, pady=20)

        # Header Title
        lbl_head = ctk.CTkLabel(
            content,
            text=title,
            font=FONTS["h2"],
            text_color=THEME["danger"] if is_destructive else THEME["text_dark"],
            anchor="w",
        )
        lbl_head.pack(fill="x", pady=(0, 8))

        # Main Description Message
        lbl_msg = ctk.CTkLabel(
            content,
            text=message,
            font=FONTS["body"],
            text_color=THEME["text_body"],
            wraplength=420,
            justify="left",
            anchor="w",
        )
        lbl_msg.pack(fill="x", pady=(0, 12))

        # Structured details box (if provided)
        if details:
            details_box = ctk.CTkFrame(
                content,
                fg_color=THEME["bg_main"],
                corner_radius=6,
                border_width=1,
                border_color=THEME["card_border"],
            )
            details_box.pack(fill="x", pady=(0, 16), padx=2)

            for key, val in details.items():
                row = ctk.CTkFrame(details_box, fg_color="transparent")
                row.pack(fill="x", padx=12, pady=3)

                lbl_k = ctk.CTkLabel(
                    row,
                    text=f"{key}:",
                    font=FONTS["small_bold"],
                    text_color=THEME["text_muted"],
                    width=110,
                    anchor="w",
                )
                lbl_k.pack(side="left")

                lbl_v = ctk.CTkLabel(
                    row,
                    text=str(val),
                    font=FONTS["small"],
                    text_color=THEME["text_dark"],
                    anchor="w",
                )
                lbl_v.pack(side="left", fill="x", expand=True)

        # Action Buttons
        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.pack(fill="x", side="bottom", pady=(10, 0))

        # Cancel Button
        self.btn_cancel = ctk.CTkButton(
            btn_frame,
            text=cancel_text,
            font=FONTS["body_bold"],
            fg_color=THEME["bg_main"],
            text_color=THEME["text_body"],
            hover_color=THEME["table_header_bg"],
            border_width=1,
            border_color=THEME["card_border"],
            height=36,
            command=self._on_cancel,
        )
        self.btn_cancel.pack(side="right", padx=(8, 0))

        # Confirm Button
        confirm_bg = THEME["danger"] if is_destructive else THEME["primary"]
        confirm_hover = "#B91C1C" if is_destructive else THEME["primary_hover"]
        self.btn_confirm = ctk.CTkButton(
            btn_frame,
            text=confirm_text,
            font=FONTS["body_bold"],
            fg_color=confirm_bg,
            hover_color=confirm_hover,
            text_color="#FFFFFF",
            height=36,
            command=self._on_confirm,
        )
        self.btn_confirm.pack(side="right")

        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.wait_window()

    def _on_confirm(self):
        self.confirmed = True
        self.destroy()

    def _on_cancel(self):
        self.confirmed = False
        self.destroy()

    @classmethod
    def ask(
        cls,
        parent,
        title: str,
        message: str,
        details: Optional[Dict[str, str]] = None,
        confirm_text: str = "Confirm",
        cancel_text: str = "Cancel",
        is_destructive: bool = False,
    ) -> bool:
        """Helper static method to launch dialog and return boolean result."""
        dialog = cls(
            parent=parent,
            title=title,
            message=message,
            details=details,
            confirm_text=confirm_text,
            cancel_text=cancel_text,
            is_destructive=is_destructive,
        )
        return dialog.confirmed
