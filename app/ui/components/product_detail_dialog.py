"""Product Detail Deep-Link Modal with comprehensive specifications and working edit action."""

from typing import Callable, Optional
import customtkinter as ctk

from app.models.product import Product
from app.services import product_service, inventory_service
from app.ui.theme import THEME, FONTS


class ProductDetailDialog(ctk.CTkToplevel):
    """Deep-link view displaying comprehensive product metrics, history, and edit controls."""

    def __init__(
        self,
        parent,
        product: Product,
        on_data_change: Optional[Callable[[], None]] = None,
    ):
        super().__init__(parent)

        self.parent = parent
        self.product = product
        self.on_data_change = on_data_change

        self.title(f"Product Details — {product.product_id} ({product.name})")
        self.geometry("680x720")
        self.minsize(620, 650)
        self.configure(fg_color=THEME["card_bg"])

        self.transient(parent)
        self.grab_set()

        # Center on parent
        self.update_idletasks()
        try:
            x = parent.winfo_x() + (parent.winfo_width() - 680) // 2
            y = parent.winfo_y() + (parent.winfo_height() - 720) // 2
            self.geometry(f"+{max(0, x)}+{max(0, y)}")
        except Exception:
            pass

        self._build_ui()

    def _build_ui(self):
        # 1. Header Banner
        header = ctk.CTkFrame(self, fg_color=THEME["sidebar_bg"], height=70, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)

        h_left = ctk.CTkFrame(header, fg_color="transparent")
        h_left.pack(side="left", padx=20, pady=10)

        lbl_id = ctk.CTkLabel(
            h_left,
            text=f"{self.product.product_id} • SKU: {self.product.sku}",
            font=FONTS["small_bold"],
            text_color="#38BDF8",  # Sky 400
            anchor="w",
        )
        lbl_id.pack(anchor="w")

        self.lbl_title = ctk.CTkLabel(
            h_left,
            text=self.product.name,
            font=FONTS["h2"],
            text_color="#FFFFFF",
            anchor="w",
        )
        self.lbl_title.pack(anchor="w")

        # Health badge on top right
        h_right = ctk.CTkFrame(header, fg_color="transparent")
        h_right.pack(side="right", padx=20, pady=16)

        if self.product.quantity == 0:
            badge_text = "OUT OF STOCK"
            badge_color = THEME["danger"]
        elif self.product.is_low_stock:
            badge_text = "LOW STOCK ALERT"
            badge_color = THEME["warning"]
        else:
            badge_text = "STOCK HEALTHY"
            badge_color = THEME["success"]

        self.health_badge = ctk.CTkLabel(
            h_right,
            text=f" ● {badge_text} ",
            font=FONTS["small_bold"],
            fg_color=badge_color,
            text_color="#FFFFFF",
            corner_radius=6,
            height=28,
            padx=10,
        )
        self.health_badge.pack(side="right")

        # 2. Main Scrollable Container
        self.body = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.body.pack(fill="both", expand=True, padx=20, pady=14)

        # 3. Four KPI Metric Cards
        kpi_grid = ctk.CTkFrame(self.body, fg_color="transparent")
        kpi_grid.pack(fill="x", pady=(0, 14))
        kpi_grid.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self._render_kpi_card(kpi_grid, 0, "Current Stock", f"{self.product.quantity} Units", THEME["primary"])
        self._render_kpi_card(kpi_grid, 1, "Unit Price", f"${self.product.unit_price:.2f}", THEME["text_dark"])
        self._render_kpi_card(kpi_grid, 2, "Line Valuation", f"${self.product.total_valuation:,.2f}", THEME["success"])
        self._render_kpi_card(kpi_grid, 3, "Reorder Level", f"{self.product.reorder_level} Units", THEME["warning"])

        # 4. Specifications Card
        spec_card = ctk.CTkFrame(
            self.body,
            fg_color=THEME["bg_main"],
            corner_radius=8,
            border_width=1,
            border_color=THEME["card_border"],
        )
        spec_card.pack(fill="x", pady=(0, 14), ipadx=14, ipady=12)

        lbl_spec_title = ctk.CTkLabel(
            spec_card,
            text="PRODUCT SPECIFICATIONS & ATTRIBUTES",
            font=FONTS["small_bold"],
            text_color=THEME["text_muted"],
            anchor="w",
        )
        lbl_spec_title.pack(fill="x", padx=14, pady=(4, 10))

        spec_grid = ctk.CTkFrame(spec_card, fg_color="transparent")
        spec_grid.pack(fill="x", padx=14)
        spec_grid.grid_columnconfigure((0, 1), weight=1)

        self._add_spec_item(spec_grid, 0, 0, "Category", self.product.category)
        self._add_spec_item(spec_grid, 0, 1, "SKU Identifier", self.product.sku)
        self._add_spec_item(spec_grid, 1, 0, "Supplier / Vendor", self.product.supplier_name)
        self._add_spec_item(spec_grid, 1, 1, "Registration Date", self.product.created_at)
        self._add_spec_item(spec_grid, 2, 0, "Last Updated", self.product.updated_at)
        self._add_spec_item(spec_grid, 2, 1, "Reorder Required?", "YES (Order Required)" if self.product.is_low_stock else "NO (Sufficient)")

        # 5. Recent Stock Movement History for this product
        hist_card = ctk.CTkFrame(
            self.body,
            fg_color=THEME["bg_main"],
            corner_radius=8,
            border_width=1,
            border_color=THEME["card_border"],
        )
        hist_card.pack(fill="x", pady=(0, 10), ipadx=14, ipady=12)

        lbl_hist_title = ctk.CTkLabel(
            hist_card,
            text="RECENT AUDITED MOVEMENTS FOR THIS PRODUCT",
            font=FONTS["small_bold"],
            text_color=THEME["text_muted"],
            anchor="w",
        )
        lbl_hist_title.pack(fill="x", padx=14, pady=(4, 8))

        # Query movements
        movements = inventory_service.get_stock_movements(product_id=self.product.product_id, limit=5)
        if movements:
            for mov in movements:
                m_frame = ctk.CTkFrame(hist_card, fg_color=THEME["card_bg"], corner_radius=6)
                m_frame.pack(fill="x", padx=10, pady=3, ipadx=6, ipady=4)

                m_type = mov.movement_type
                m_color = THEME["success"] if m_type in ("IN", "INITIAL") else (THEME["danger"] if m_type == "OUT" else THEME["warning"])

                tag = ctk.CTkLabel(
                    m_frame,
                    text=f" {m_type} ",
                    font=FONTS["small_bold"],
                    fg_color=m_color,
                    text_color="#FFFFFF",
                    corner_radius=4,
                    width=50,
                )
                tag.pack(side="left", padx=(6, 10))

                delta_str = f"+{mov.quantity_change}" if mov.quantity_change > 0 else str(mov.quantity_change)
                qty_lbl = ctk.CTkLabel(
                    m_frame,
                    text=f"Change: {delta_str} (Balance: {mov.new_quantity})",
                    font=FONTS["body_bold"],
                    text_color=THEME["text_dark"],
                )
                qty_lbl.pack(side="left", padx=4)

                reason_lbl = ctk.CTkLabel(
                    m_frame,
                    text=f"• {mov.reason}",
                    font=FONTS["small"],
                    text_color=THEME["text_muted"],
                )
                reason_lbl.pack(side="left", padx=8)

                ts_lbl = ctk.CTkLabel(
                    m_frame,
                    text=mov.timestamp,
                    font=FONTS["small"],
                    text_color=THEME["text_muted"],
                )
                ts_lbl.pack(side="right", padx=10)
        else:
            lbl_empty = ctk.CTkLabel(
                hist_card,
                text="No stock movements recorded for this item yet.",
                font=FONTS["small"],
                text_color=THEME["text_muted"],
            )
            lbl_empty.pack(padx=14, pady=6)

        # 6. Bottom Action Bar (Working Edit Button + Adjust Button + Close)
        action_bar = ctk.CTkFrame(self, fg_color=THEME["table_header_bg"], height=60, corner_radius=0)
        action_bar.pack(fill="x", side="bottom")

        btn_close = ctk.CTkButton(
            action_bar,
            text="Close",
            font=FONTS["body"],
            fg_color=THEME["card_bg"],
            text_color=THEME["text_body"],
            border_width=1,
            border_color=THEME["card_border"],
            hover_color=THEME["bg_main"],
            height=36,
            width=90,
            command=self.destroy,
        )
        btn_close.pack(side="right", padx=16, pady=12)

        # Working Edit Product Button
        btn_edit = ctk.CTkButton(
            action_bar,
            text="✏️ Edit Product Information",
            font=FONTS["body_bold"],
            fg_color=THEME["primary"],
            hover_color=THEME["primary_hover"],
            height=36,
            command=self._handle_edit_click,
        )
        btn_edit.pack(side="right", padx=4, pady=12)

        # Quick Adjust Stock Button
        btn_adjust = ctk.CTkButton(
            action_bar,
            text="⚖️ Adjust Stock Level",
            font=FONTS["body"],
            fg_color=THEME["warning"],
            hover_color=THEME["warning_hover"],
            text_color="#FFFFFF",
            height=36,
            command=self._handle_adjust_click,
        )
        btn_adjust.pack(side="right", padx=4, pady=12)

    def _render_kpi_card(self, parent, col, title, value, accent_color):
        card = ctk.CTkFrame(
            parent,
            fg_color=THEME["bg_main"],
            corner_radius=8,
            border_width=1,
            border_color=THEME["card_border"],
        )
        card.grid(row=0, column=col, padx=4, sticky="nsew", ipady=8)

        ctk.CTkLabel(card, text=title.upper(), font=FONTS["small_bold"], text_color=THEME["text_muted"]).pack(pady=(4, 2))
        ctk.CTkLabel(card, text=value, font=FONTS["h3"], text_color=accent_color).pack(pady=(0, 4))

    def _add_spec_item(self, parent, row, col, label, val):
        box = ctk.CTkFrame(parent, fg_color="transparent")
        box.grid(row=row, column=col, padx=8, pady=4, sticky="ew")

        ctk.CTkLabel(box, text=label, font=FONTS["small_bold"], text_color=THEME["text_muted"], anchor="w").pack(anchor="w")
        ctk.CTkLabel(box, text=str(val), font=FONTS["body_bold"], text_color=THEME["text_dark"], anchor="w").pack(anchor="w")

    def _handle_edit_click(self):
        """Launches the edit dialog and refreshes on save."""
        from app.ui.views.products_view import ProductModalDialog

        def on_saved(updated_product: Optional[Product]):
            if updated_product:
                # Reload fresh product from DB
                fresh = product_service.get_product_by_id(self.product.product_id)
                if fresh:
                    self.product = fresh
                    # Rebuild UI
                    for child in self.winfo_children():
                        child.destroy()
                    self._build_ui()
            if self.on_data_change:
                self.on_data_change()

        ProductModalDialog(self, product=self.product, on_save_success=on_saved)

    def _handle_adjust_click(self):
        """Launches stock adjustment dialog for this product."""
        from app.ui.views.inventory_view import StockAdjustmentModal

        def on_adjusted():
            fresh = product_service.get_product_by_id(self.product.product_id)
            if fresh:
                self.product = fresh
                for child in self.winfo_children():
                    child.destroy()
                self._build_ui()
            if self.on_data_change:
                self.on_data_change()

        StockAdjustmentModal(self, product=self.product, on_success=on_adjusted)
