"""StatCard component for dashboard KPI metric tiles."""

import customtkinter as ctk
from app.ui.theme import THEME, FONTS


class StatCard(ctk.CTkFrame):
    """Modern enterprise KPI metric display card."""

    def __init__(
        self,
        master,
        title: str,
        value: str,
        subtitle: str = "",
        accent_color: str = THEME["primary"],
        icon_text: str = "",
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

        self.accent_color = accent_color

        # Top Accent stripe
        self.stripe = ctk.CTkFrame(
            self,
            fg_color=accent_color,
            height=4,
            corner_radius=2,
        )
        self.stripe.pack(fill="x", padx=10, pady=(6, 4))

        # Content Container
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=16, pady=(4, 12))

        # Title row
        self.title_row = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.title_row.pack(fill="x")

        self.lbl_title = ctk.CTkLabel(
            self.title_row,
            text=title.upper(),
            font=FONTS["small_bold"],
            text_color=THEME["text_muted"],
            anchor="w",
        )
        self.lbl_title.pack(side="left")

        if icon_text:
            self.lbl_icon = ctk.CTkLabel(
                self.title_row,
                text=icon_text,
                font=FONTS["small_bold"],
                text_color=accent_color,
                anchor="e",
            )
            self.lbl_icon.pack(side="right")

        # Big Value label
        self.lbl_value = ctk.CTkLabel(
            self.content_frame,
            text=value,
            font=FONTS["metric"],
            text_color=THEME["text_dark"],
            anchor="w",
        )
        self.lbl_value.pack(fill="x", pady=(4, 2))

        # Subtitle
        self.lbl_subtitle = ctk.CTkLabel(
            self.content_frame,
            text=subtitle,
            font=FONTS["small"],
            text_color=THEME["text_muted"],
            anchor="w",
        )
        self.lbl_subtitle.pack(fill="x")

    def update_values(self, value: str, subtitle: str = "") -> None:
        """Updates the metric values dynamically."""
        self.lbl_value.configure(text=value)
        if subtitle:
            self.lbl_subtitle.configure(text=subtitle)
