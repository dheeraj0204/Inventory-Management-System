"""Main Application Window with enterprise navigation sidebar and dynamic view container."""

from typing import Callable, Dict, Optional
import customtkinter as ctk

from app.config import (
    APP_TITLE,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    MIN_WINDOW_WIDTH,
    MIN_WINDOW_HEIGHT,
)
from app.models.user import User
from app.services.auth_service import auth_service
from app.ui.theme import THEME, FONTS
from app.ui.views import DashboardView, ProductsView, InventoryView, AuditView, TQMView


class AppWindow(ctk.CTk):
    """Main desktop application window container."""

    def __init__(
        self,
        current_user: Optional[User] = None,
        on_logout: Optional[Callable[[], None]] = None,
    ):
        super().__init__()

        self.current_user = current_user or auth_service.get_current_user()
        self.on_logout = on_logout

        # Appearance & Window Configuration
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.title(APP_TITLE)
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
        self.configure(fg_color=THEME["bg_main"])

        # State tracking
        self.current_view_key = "dashboard"
        self.views: Dict[str, ctk.CTkFrame] = {}
        self.nav_buttons: Dict[str, ctk.CTkButton] = {}

        self._build_layout()
        self.switch_view("dashboard")

    def _build_layout(self):
        # Grid Layout: Column 0 = Sidebar (fixed width), Column 1 = Main Content (expandable)
        self.grid_columnconfigure(0, weight=0, minsize=240)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 1. Sidebar Container
        self.sidebar = ctk.CTkFrame(
            self,
            fg_color=THEME["sidebar_bg"],
            corner_radius=0,
            width=240,
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        self._build_sidebar()

        # 2. Main Content Container
        self.main_container = ctk.CTkFrame(
            self,
            fg_color=THEME["bg_main"],
            corner_radius=0,
        )
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        # Instantiate all Views lazily or upfront
        self.views["dashboard"] = DashboardView(
            self.main_container,
            nav_callback=self.switch_view,
        )
        self.views["products"] = ProductsView(
            self.main_container,
            on_data_change=self._notify_data_changed,
        )
        self.views["inventory"] = InventoryView(
            self.main_container,
            on_data_change=self._notify_data_changed,
        )
        self.views["audit"] = AuditView(
            self.main_container,
        )
        self.views["tqm"] = TQMView(
            self.main_container,
        )

    def _build_sidebar(self):
        # App Branding & Title
        brand_box = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand_box.pack(fill="x", padx=16, pady=(20, 16))

        badge = ctk.CTkLabel(
            brand_box,
            text="ENTERPRISE INVENTORY",
            font=FONTS["small_bold"],
            text_color="#38BDF8",  # Sky 400
            anchor="w",
        )
        badge.pack(fill="x")

        title = ctk.CTkLabel(
            brand_box,
            text="Inventory IMS",
            font=FONTS["h1"],
            text_color=THEME["sidebar_text"],
            anchor="w",
        )
        title.pack(fill="x", pady=(2, 0))

        sub = ctk.CTkLabel(
            brand_box,
            text="Stock Control & Audit Platform",
            font=FONTS["small"],
            text_color="#94A3B8",
            anchor="w",
        )
        sub.pack(fill="x")

        # Divider
        div = ctk.CTkFrame(self.sidebar, fg_color=THEME["sidebar_border"], height=1)
        div.pack(fill="x", padx=16, pady=(0, 16))

        # Nav Section Label
        lbl_nav = ctk.CTkLabel(
            self.sidebar,
            text="MAIN NAVIGATION",
            font=FONTS["small_bold"],
            text_color=THEME["sidebar_text_muted"],
            anchor="w",
        )
        lbl_nav.pack(fill="x", padx=20, pady=(0, 6))

        # Navigation Buttons
        nav_items = [
            ("dashboard", "📊  Dashboard Overview"),
            ("products", "📦  Product Catalog"),
            ("inventory", "⚖️  Inventory & Stock"),
            ("audit", "📜  Audit History"),
            ("tqm", "🎯  Quality & Analytics"),
        ]

        for key, label in nav_items:
            btn = ctk.CTkButton(
                self.sidebar,
                text=label,
                font=FONTS["body_bold"],
                anchor="w",
                fg_color="transparent",
                text_color=THEME["sidebar_text_muted"],
                hover_color=THEME["sidebar_hover"],
                height=42,
                corner_radius=THEME["button_radius"],
                command=lambda k=key: self.switch_view(k),
            )
            btn.pack(fill="x", padx=12, pady=3)
            self.nav_buttons[key] = btn

        # Bottom User Profile & Sign Out Box
        user_card = ctk.CTkFrame(
            self.sidebar,
            fg_color="#090E17",
            corner_radius=8,
            border_width=1,
            border_color=THEME["sidebar_border"],
        )
        user_card.pack(fill="x", side="bottom", padx=12, pady=16)

        user_name = self.current_user.full_name if self.current_user else "System Administrator"
        user_role = self.current_user.role if self.current_user else "Admin"
        user_handle = f"@{self.current_user.username}" if self.current_user else "@admin"

        ctk.CTkLabel(
            user_card,
            text=f"👤 {user_name}",
            font=FONTS["body_bold"],
            text_color="#F8FAFC",
            anchor="w",
        ).pack(fill="x", padx=10, pady=(8, 1))

        ctk.CTkLabel(
            user_card,
            text=f"{user_role} • {user_handle}",
            font=FONTS["small"],
            text_color="#38BDF8",
            anchor="w",
        ).pack(fill="x", padx=10, pady=(0, 8))

        btn_logout = ctk.CTkButton(
            user_card,
            text="🚪 Sign Out / Logout",
            font=FONTS["small_bold"],
            fg_color="#1E293B",
            hover_color=THEME["danger"],
            text_color="#FCA5A5",
            height=30,
            corner_radius=4,
            command=self._handle_logout,
        )
        btn_logout.pack(fill="x", padx=8, pady=(0, 8))

    def _handle_logout(self):
        """Terminates session, closes main window, and returns to authentication."""
        auth_service.logout()
        self.destroy()
        if self.on_logout:
            self.on_logout()

    def switch_view(self, view_key: str):
        """Swaps the active view in the main container and updates sidebar styling."""
        if view_key not in self.views:
            return

        # Hide current view
        if self.current_view_key in self.views:
            self.views[self.current_view_key].grid_forget()

        # Update sidebar button states
        for key, btn in self.nav_buttons.items():
            if key == view_key:
                btn.configure(
                    fg_color=THEME["sidebar_active"],
                    text_color="#FFFFFF",
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=THEME["sidebar_text_muted"],
                )

        # Show target view
        target_view = self.views[view_key]
        target_view.grid(row=0, column=0, sticky="nsew")
        self.current_view_key = view_key

        # Trigger refresh on view entry
        if hasattr(target_view, "refresh"):
            target_view.refresh()

    def _notify_data_changed(self):
        """Broadcasts data modification event to refresh dependent views."""
        for key, view in self.views.items():
            if hasattr(view, "refresh") and key != self.current_view_key:
                view.refresh()
