"""Inventory Management View: Stock adjustments, low-stock alerts, and movement history."""

from typing import Any, Callable, Dict, List, Optional
import customtkinter as ctk

from app.config import STOCK_ADJUSTMENT_REASONS
from app.models.product import Product
from app.services import inventory_service, product_service
from app.ui.components import ConfirmDialog, TableView, ProductDetailDialog
from app.ui.theme import THEME, FONTS
from app.utils.validators import ProductValidator, ValidationError


class StockAdjustmentModal(ctk.CTkToplevel):
    """Modal dialog for executing audited stock adjustments with live variance preview."""

    def __init__(
        self,
        parent,
        product: Optional[Product] = None,
        on_success: Optional[Callable[[], None]] = None,
    ):
        super().__init__(parent)

        self.selected_product = product
        self.on_success = on_success
        self.all_products = product_service.get_all_products()

        self.title("Execute Audited Stock Adjustment")
        self.geometry("520x540")
        self.resizable(False, False)
        self.configure(fg_color=THEME["card_bg"])

        self.transient(parent)
        self.grab_set()

        # Center on parent
        self.update_idletasks()
        try:
            x = parent.winfo_x() + (parent.winfo_width() - 520) // 2
            y = parent.winfo_y() + (parent.winfo_height() - 540) // 2
            self.geometry(f"+{max(0, x)}+{max(0, y)}")
        except Exception:
            pass

        self._build_ui()

    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color=THEME["warning"], height=48, corner_radius=0)
        header.pack(fill="x")

        lbl_head = ctk.CTkLabel(
            header,
            text="STOCK LEVEL AUDIT ADJUSTMENT",
            font=FONTS["h3"],
            text_color="#FFFFFF",
        )
        lbl_head.pack(side="left", padx=20, pady=12)

        # Body
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=24, pady=16)

        # Inline Error Banner
        self.error_frame = ctk.CTkFrame(
            body,
            fg_color=THEME["danger_bg"],
            border_width=1,
            border_color=THEME["danger"],
            corner_radius=6,
        )
        self.lbl_error = ctk.CTkLabel(
            self.error_frame,
            text="",
            font=FONTS["small_bold"],
            text_color=THEME["danger"],
            wraplength=440,
            justify="left",
        )
        self.lbl_error.pack(fill="x", padx=12, pady=8)

        # 1. Product Selector Dropdown
        lbl_sel = ctk.CTkLabel(body, text="Select Product to Adjust *", font=FONTS["small_bold"], text_color=THEME["text_body"])
        lbl_sel.pack(anchor="w")

        prod_options = [f"{p.product_id} - {p.name} ({p.sku})" for p in self.all_products]
        self.combo_prod = ctk.CTkOptionMenu(
            body,
            values=prod_options if prod_options else ["No products available"],
            height=34,
            font=FONTS["body"],
            fg_color=THEME["bg_main"],
            button_color=THEME["secondary"],
            button_hover_color=THEME["secondary_hover"],
            text_color=THEME["text_dark"],
            dropdown_text_color=THEME["text_dark"],
            dropdown_fg_color="#FFFFFF",
            command=self._on_product_dropdown_changed,
        )
        if self.selected_product:
            matched = f"{self.selected_product.product_id} - {self.selected_product.name} ({self.selected_product.sku})"
            self.combo_prod.set(matched)
        elif prod_options:
            self.combo_prod.set(prod_options[0])
            self._update_selected_product_from_dropdown(prod_options[0])
        self.combo_prod.pack(fill="x", pady=(2, 12))

        # Current Stock display card
        self.info_box = ctk.CTkFrame(body, fg_color=THEME["bg_main"], corner_radius=6, border_width=1, border_color=THEME["card_border"])
        self.info_box.pack(fill="x", pady=(0, 12))

        self.lbl_cur_stock = ctk.CTkLabel(
            self.info_box,
            text=f"Current Verified Stock: {self.selected_product.quantity if self.selected_product else 0} units",
            font=FONTS["body_bold"],
            text_color=THEME["primary"],
        )
        self.lbl_cur_stock.pack(padx=12, pady=8, anchor="w")

        # 2. New Quantity Input
        lbl_new = ctk.CTkLabel(body, text="New Verified Physical Quantity * (Integer >= 0)", font=FONTS["small_bold"], text_color=THEME["text_body"])
        lbl_new.pack(anchor="w")

        self.entry_new_qty = ctk.CTkEntry(
            body,
            placeholder_text="Enter physical count result...",
            height=34,
            font=FONTS["body"],
            border_color=THEME["card_border"],
        )
        self.entry_new_qty.pack(fill="x", pady=(2, 8))
        self.entry_new_qty.bind("<KeyRelease>", self._on_qty_type)

        # Live Variance Preview
        self.lbl_variance = ctk.CTkLabel(
            body,
            text="Adjustment Variance: 0 units (No Change)",
            font=FONTS["small_bold"],
            text_color=THEME["text_muted"],
            anchor="w",
        )
        self.lbl_variance.pack(fill="x", pady=(0, 12))

        # 3. Adjustment Reason (Controlled standard options)
        lbl_r = ctk.CTkLabel(body, text="Mandatory Reason for Stock Adjustment *", font=FONTS["small_bold"], text_color=THEME["text_body"])
        lbl_r.pack(anchor="w")

        self.combo_reason = ctk.CTkOptionMenu(
            body,
            values=STOCK_ADJUSTMENT_REASONS,
            height=34,
            font=FONTS["body"],
            fg_color=THEME["bg_main"],
            button_color=THEME["secondary"],
            button_hover_color=THEME["secondary_hover"],
            text_color=THEME["text_dark"],
            dropdown_text_color=THEME["text_dark"],
            dropdown_fg_color="#FFFFFF",
        )
        self.combo_reason.set(STOCK_ADJUSTMENT_REASONS[0])
        self.combo_reason.pack(fill="x", pady=(2, 16))

        # Bottom Buttons
        bottom_bar = ctk.CTkFrame(self, fg_color="transparent")
        bottom_bar.pack(fill="x", padx=24, pady=16)

        btn_cancel = ctk.CTkButton(
            bottom_bar,
            text="Cancel",
            font=FONTS["body"],
            fg_color=THEME["bg_main"],
            text_color=THEME["text_body"],
            border_width=1,
            border_color=THEME["card_border"],
            hover_color=THEME["table_header_bg"],
            height=36,
            command=self.destroy,
        )
        btn_cancel.pack(side="right", padx=(8, 0))

        btn_apply = ctk.CTkButton(
            bottom_bar,
            text="Apply Adjustment",
            font=FONTS["body_bold"],
            fg_color=THEME["warning"],
            hover_color="#B45309",
            text_color="#FFFFFF",
            height=36,
            command=self._handle_apply,
        )
        btn_apply.pack(side="right")

    def _on_product_dropdown_changed(self, selection_str: str):
        self._update_selected_product_from_dropdown(selection_str)

    def _update_selected_product_from_dropdown(self, selection_str: str):
        pid = selection_str.split(" - ")[0].strip()
        self.selected_product = product_service.get_product_by_id(pid)
        if self.selected_product:
            self.lbl_cur_stock.configure(text=f"Current Verified Stock: {self.selected_product.quantity} units")
            self._update_variance_preview()

    def _on_qty_type(self, event):
        self._update_variance_preview()

    def _update_variance_preview(self):
        if not self.selected_product:
            return
        val_str = self.entry_new_qty.get().strip()
        try:
            new_q = int(val_str)
            diff = new_q - self.selected_product.quantity
            if diff > 0:
                self.lbl_variance.configure(
                    text=f"Adjustment Variance: +{diff} units (Stock Inward / Correction)",
                    text_color=THEME["success"],
                )
            elif diff < 0:
                self.lbl_variance.configure(
                    text=f"Adjustment Variance: {diff} units (Stock Outward / Write-off)",
                    text_color=THEME["danger"],
                )
            else:
                self.lbl_variance.configure(
                    text="Adjustment Variance: 0 units (No Change)",
                    text_color=THEME["text_muted"],
                )
        except Exception:
            self.lbl_variance.configure(
                text="Adjustment Variance: Invalid numeric input",
                text_color=THEME["danger"],
            )

    def _handle_apply(self):
        self.error_frame.pack_forget()

        if not self.selected_product:
            self._show_error("No product selected.")
            return

        qty_str = self.entry_new_qty.get().strip()
        reason = self.combo_reason.get().strip()

        try:
            new_qty = ProductValidator.validate_quantity(qty_str)
            if new_qty == self.selected_product.quantity:
                self._show_error(f"New quantity ({new_qty}) matches existing stock. No adjustment needed.")
                return

            diff = new_qty - self.selected_product.quantity

            # Q07 Feature 4: Confirmation Dialog before modifying database
            confirmed = ConfirmDialog.ask(
                self,
                title="Confirm Stock Adjustment",
                message=f"Are you sure you want to adjust stock for '{self.selected_product.name}'? This change will be permanently logged in the audit trail and movement ledger.",
                details={
                    "Product ID": self.selected_product.product_id,
                    "Product Name": self.selected_product.name,
                    "Previous Stock": f"{self.selected_product.quantity} units",
                    "New Stock": f"{new_qty} units",
                    "Variance": f"{'+' if diff > 0 else ''}{diff} units",
                    "Reason": reason,
                },
                confirm_text="Confirm Adjustment",
                is_destructive=False,
            )

            if not confirmed:
                return

            inventory_service.adjust_stock(
                product_id=self.selected_product.product_id,
                new_quantity=new_qty,
                reason=reason,
            )

            if self.on_success:
                self.on_success()
            self.destroy()

        except ValidationError as e:
            self._show_error(e.message)
        except Exception as ex:
            self._show_error(str(ex))

    def _show_error(self, message: str):
        self.lbl_error.configure(text=f"Adjustment Error: {message}")
        self.error_frame.pack(fill="x", pady=(0, 10), before=self.combo_prod)


class InventoryView(ctk.CTkFrame):
    """Inventory Management View with stock monitoring, adjustments, and movement history."""

    def __init__(self, master, on_data_change: Optional[Callable[[], None]] = None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self.on_data_change = on_data_change
        self.show_only_low_stock = False

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
            text="Inventory Levels & Stock Movements",
            font=FONTS["h1"],
            text_color=THEME["text_dark"],
        )
        lbl_title.pack(anchor="w")

        lbl_sub = ctk.CTkLabel(
            title_box,
            text="Formula: Valuation = Sum(Qty × Unit Price) • Audited Stock Adjustments",
            font=FONTS["small"],
            text_color=THEME["text_muted"],
        )
        lbl_sub.pack(anchor="w")

        btn_adjust = ctk.CTkButton(
            header,
            text="⚡ Adjust Stock Level",
            font=FONTS["body_bold"],
            fg_color=THEME["warning"],
            hover_color="#B45309",
            height=36,
            command=self._open_adjust_modal,
        )
        btn_adjust.pack(side="right")

        # 2. Tabs: (1) Current Stock & Valuation, (2) Stock Movement Ledger
        self.tabview = ctk.CTkTabview(
            self,
            fg_color=THEME["card_bg"],
            segmented_button_selected_color=THEME["primary"],
            segmented_button_selected_hover_color=THEME["primary_hover"],
            corner_radius=THEME["card_radius"],
        )
        self.tabview.pack(fill="both", expand=True)

        self.tab_stock = self.tabview.add("Stock Valuation & Alerts")
        self.tab_movements = self.tabview.add("Stock Movement Ledger")

        self._build_stock_tab()
        self._build_movements_tab()

    def _build_stock_tab(self):
        # Top toolbar for Stock tab
        toolbar = ctk.CTkFrame(self.tab_stock, fg_color="transparent", height=44)
        toolbar.pack(fill="x", padx=12, pady=(8, 8))

        self.btn_filter_low = ctk.CTkButton(
            toolbar,
            text="⚠️ Show Low Stock Only",
            font=FONTS["small_bold"],
            fg_color=THEME["bg_main"],
            text_color=THEME["danger"],
            border_width=1,
            border_color=THEME["card_border"],
            hover_color=THEME["danger_bg"],
            height=32,
            command=self._toggle_low_stock_filter,
        )
        self.btn_filter_low.pack(side="left")

        self.lbl_stock_count = ctk.CTkLabel(
            toolbar,
            text="Total items: 0",
            font=FONTS["small"],
            text_color=THEME["text_muted"],
        )
        self.lbl_stock_count.pack(side="right")

        # Table
        cols = [
            {"key": "product_id", "title": "ID", "width": 80, "align": "w"},
            {"key": "name", "title": "Product Name", "width": 220, "align": "w"},
            {"key": "category", "title": "Category", "width": 110, "align": "w"},
            {"key": "sku", "title": "SKU", "width": 120, "align": "w"},
            {"key": "quantity", "title": "Current Qty", "width": 80, "align": "center"},
            {"key": "reorder_level", "title": "Reorder Lvl", "width": 80, "align": "center"},
            {"key": "unit_price", "title": "Unit Price", "width": 85, "align": "e"},
            {"key": "valuation", "title": "Valuation", "width": 100, "align": "e"},
            {"key": "status", "title": "Stock Health", "width": 95, "align": "center"},
        ]
        self.table_stock = TableView(
            self.tab_stock,
            columns=cols,
            on_select=self._on_stock_row_click,
        )
        self.table_stock.pack(fill="both", expand=True, padx=8, pady=(0, 8))

    def _build_movements_tab(self):
        toolbar = ctk.CTkFrame(self.tab_movements, fg_color="transparent", height=44)
        toolbar.pack(fill="x", padx=12, pady=(8, 8))

        lbl_info = ctk.CTkLabel(
            toolbar,
            text="Traceable record of all inward, outward, and manual stock adjustment transitions.",
            font=FONTS["small"],
            text_color=THEME["text_muted"],
        )
        lbl_info.pack(side="left")

        cols = [
            {"key": "timestamp", "title": "Timestamp (UTC)", "width": 140, "align": "w"},
            {"key": "product_id", "title": "Product ID", "width": 80, "align": "w"},
            {"key": "product_name", "title": "Product Name", "width": 180, "align": "w"},
            {"key": "movement_type", "title": "Type", "width": 65, "align": "center"},
            {"key": "quantity_change", "title": "Change", "width": 65, "align": "center"},
            {"key": "previous_quantity", "title": "Prev", "width": 60, "align": "center"},
            {"key": "new_quantity", "title": "New", "width": 60, "align": "center"},
            {"key": "reason", "title": "Reason for Movement", "width": 240, "align": "w"},
        ]
        self.table_movements = TableView(self.tab_movements, columns=cols)
        self.table_movements.pack(fill="both", expand=True, padx=8, pady=(0, 8))

    def refresh(self):
        """Refreshes both Stock and Movements tables."""
        # 1. Stock table
        all_prods = product_service.get_all_products()
        if self.show_only_low_stock:
            prods = [p for p in all_prods if p.is_low_stock]
        else:
            prods = all_prods

        stock_rows = []
        for p in prods:
            health_str = "CRITICAL" if p.quantity == 0 else ("REORDER" if p.is_low_stock else "OPTIMAL")
            stock_rows.append({
                "product_id": p.product_id,
                "name": p.name,
                "category": p.category,
                "sku": p.sku,
                "quantity": p.quantity,
                "reorder_level": p.reorder_level,
                "unit_price": f"${p.unit_price:.2f}",
                "valuation": f"${p.total_valuation:,.2f}",
                "status": health_str,
                "_raw": p,
            })

        action_buttons = [
            {"name": "view", "label": "👁️ Details", "color": THEME["secondary"], "width": 72},
            {"name": "adjust", "label": "Adjust", "color": THEME["warning"], "width": 55},
        ]

        self.table_stock.set_data(
            rows=stock_rows,
            action_callback=self._handle_stock_action,
            action_buttons=action_buttons,
        )
        self.lbl_stock_count.configure(text=f"Total items: {len(stock_rows)}")

        # 2. Movements table
        movements = inventory_service.get_stock_movements(limit=100)
        mov_rows = []
        for m in movements:
            chg = m["quantity_change"]
            chg_str = f"+{chg}" if chg > 0 else str(chg)
            mov_rows.append({
                "timestamp": m["timestamp"],
                "product_id": m["product_id"],
                "product_name": m.get("product_name") or "--",
                "movement_type": m["movement_type"],
                "quantity_change": chg_str,
                "previous_quantity": m["previous_quantity"],
                "new_quantity": m["new_quantity"],
                "reason": m["reason"],
            })
        self.table_movements.set_data(rows=mov_rows)

    def _toggle_low_stock_filter(self):
        self.show_only_low_stock = not self.show_only_low_stock
        if self.show_only_low_stock:
            self.btn_filter_low.configure(
                text="✓ Showing Low Stock Only",
                fg_color=THEME["danger_bg"],
                border_color=THEME["danger"],
            )
        else:
            self.btn_filter_low.configure(
                text="⚠️ Show Low Stock Only",
                fg_color=THEME["bg_main"],
                border_color=THEME["card_border"],
            )
        self.refresh()

    def _open_adjust_modal(self, product: Optional[Product] = None):
        StockAdjustmentModal(self, product=product, on_success=self._on_adjusted)

    def _on_stock_row_click(self, row: Dict[str, Any]):
        """Deep-link inspection when clicking on a row in the stock table."""
        if "_raw" in row and isinstance(row["_raw"], Product):
            ProductDetailDialog(self, product=row["_raw"], on_data_change=self.refresh)

    def _handle_stock_action(self, action: str, row: Dict[str, Any]):
        product: Product = row["_raw"]
        if action == "view":
            ProductDetailDialog(self, product=product, on_data_change=self.refresh)
        elif action == "adjust":
            self._open_adjust_modal(product)

    def _on_adjusted(self):
        self.refresh()
        if self.on_data_change:
            self.on_data_change()
