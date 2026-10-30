"""Product Management View: Complete CRUD, Input Masking, Controlled Dropdowns, and Search."""

from typing import Any, Callable, Dict, List, Optional
import customtkinter as ctk

from app.config import ALLOWED_CATEGORIES
from app.models.product import Product
from app.services import product_service
from app.ui.components import AutocompleteEntry, ConfirmDialog, TableView, ProductDetailDialog
from app.ui.theme import THEME, FONTS
from app.utils.validators import ProductValidator, ValidationError


class ProductModalDialog(ctk.CTkToplevel):
    """Product Creation and Editing Modal enforcing strict Q07 validation and dropdowns."""

    def __init__(
        self,
        parent,
        product: Optional[Product] = None,
        on_save_success: Optional[Callable[[Product], None]] = None,
    ):
        super().__init__(parent)

        self.product = product
        self.is_edit = product is not None
        self.on_save_success = on_save_success

        title_text = "Edit Product Record" if self.is_edit else "Add New Inventory Product"
        self.title(title_text)
        self.geometry("540x620")
        self.resizable(False, False)
        self.configure(fg_color=THEME["card_bg"])

        self.transient(parent)
        self.grab_set()

        # Center on parent
        self.update_idletasks()
        try:
            x = parent.winfo_x() + (parent.winfo_width() - 540) // 2
            y = parent.winfo_y() + (parent.winfo_height() - 620) // 2
            self.geometry(f"+{max(0, x)}+{max(0, y)}")
        except Exception:
            pass

        self._build_form()
        if self.is_edit:
            self._populate_fields(product)

    def _build_form(self):
        # Header banner
        header = ctk.CTkFrame(self, fg_color=THEME["primary"], height=48, corner_radius=0)
        header.pack(fill="x")

        lbl_head = ctk.CTkLabel(
            header,
            text="EDIT PRODUCT RECORD" if self.is_edit else "NEW PRODUCT REGISTRATION",
            font=FONTS["h3"],
            text_color="#FFFFFF",
        )
        lbl_head.pack(side="left", padx=20, pady=12)

        # Form Scrollable Body
        self.body = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.body.pack(fill="both", expand=True, padx=24, pady=16)

        # Inline Error Banner (Hidden until validation triggers)
        self.error_frame = ctk.CTkFrame(
            self.body,
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
            wraplength=460,
            justify="left",
        )
        self.lbl_error.pack(fill="x", padx=12, pady=8)

        # Field: Product ID (Display Only)
        self.pid_val = self.product.product_id if self.is_edit else product_service.generate_next_product_id()
        self._add_label("System Product ID (Immutable)")
        self.entry_pid = ctk.CTkEntry(
            self.body,
            height=34,
            font=FONTS["body_bold"],
            fg_color=THEME["table_header_bg"],
            text_color=THEME["text_muted"],
            border_color=THEME["card_border"],
        )
        self.entry_pid.insert(0, self.pid_val)
        self.entry_pid.configure(state="disabled")
        self.entry_pid.pack(fill="x", pady=(2, 10))

        # Field: Product Name
        self._add_label("Product Name * (2–100 characters)")
        self.entry_name = ctk.CTkEntry(
            self.body,
            placeholder_text="e.g. Precision Digital Caliper",
            height=34,
            font=FONTS["body"],
            border_color=THEME["card_border"],
        )
        self.entry_name.pack(fill="x", pady=(2, 10))

        # Field: Category (Controlled Dropdown - Q07 Feature 2)
        self._add_label("Product Category * (Controlled Master Dropdown)")
        self.combo_category = ctk.CTkOptionMenu(
            self.body,
            values=ALLOWED_CATEGORIES,
            height=34,
            font=FONTS["body"],
            fg_color=THEME["bg_main"],
            button_color=THEME["primary"],
            button_hover_color=THEME["primary_hover"],
            text_color=THEME["text_dark"],
            dropdown_text_color=THEME["text_dark"],
            dropdown_fg_color="#FFFFFF",
        )
        self.combo_category.set(ALLOWED_CATEGORIES[0])
        self.combo_category.pack(fill="x", pady=(2, 10))

        # Field: SKU Code (Q07 Feature 1 Strict Masking)
        self._add_label("SKU Code * (Unique Alphanumeric with hyphens, e.g. ELEC-CAL-01)")
        self.entry_sku = ctk.CTkEntry(
            self.body,
            placeholder_text="e.g. ELEC-CAL-01",
            height=34,
            font=FONTS["body"],
            border_color=THEME["card_border"],
        )
        self.entry_sku.pack(fill="x", pady=(2, 10))
        # Live uppercase transform on key release
        self.entry_sku.bind("<KeyRelease>", self._on_sku_type)

        # 2-Column Row: Quantity & Unit Price
        num_row = ctk.CTkFrame(self.body, fg_color="transparent")
        num_row.pack(fill="x", pady=(2, 10))
        num_row.grid_columnconfigure((0, 1), weight=1)

        # Quantity
        col_qty = ctk.CTkFrame(num_row, fg_color="transparent")
        col_qty.grid(row=0, column=0, padx=(0, 6), sticky="ew")
        lbl_q = ctk.CTkLabel(col_qty, text="Quantity in Stock * (Integer >= 0)", font=FONTS["small_bold"], text_color=THEME["text_body"])
        lbl_q.pack(anchor="w")
        self.entry_qty = ctk.CTkEntry(col_qty, placeholder_text="0", height=34, font=FONTS["body"], border_color=THEME["card_border"])
        self.entry_qty.pack(fill="x", pady=(2, 0))

        # Unit Price
        col_price = ctk.CTkFrame(num_row, fg_color="transparent")
        col_price.grid(row=0, column=1, padx=(6, 0), sticky="ew")
        lbl_p = ctk.CTkLabel(col_price, text="Unit Price ($) * (Positive > 0.00)", font=FONTS["small_bold"], text_color=THEME["text_body"])
        lbl_p.pack(anchor="w")
        self.entry_price = ctk.CTkEntry(col_price, placeholder_text="0.00", height=34, font=FONTS["body"], border_color=THEME["card_border"])
        self.entry_price.pack(fill="x", pady=(2, 0))

        # 2-Column Row: Reorder Level & Supplier Name
        sup_row = ctk.CTkFrame(self.body, fg_color="transparent")
        sup_row.pack(fill="x", pady=(2, 10))
        sup_row.grid_columnconfigure((0, 1), weight=1)

        # Reorder Level
        col_reorder = ctk.CTkFrame(sup_row, fg_color="transparent")
        col_reorder.grid(row=0, column=0, padx=(0, 6), sticky="ew")
        lbl_r = ctk.CTkLabel(col_reorder, text="Reorder Threshold (Default: 5)", font=FONTS["small_bold"], text_color=THEME["text_body"])
        lbl_r.pack(anchor="w")
        self.entry_reorder = ctk.CTkEntry(col_reorder, placeholder_text="5", height=34, font=FONTS["body"], border_color=THEME["card_border"])
        self.entry_reorder.insert(0, "5")
        self.entry_reorder.pack(fill="x", pady=(2, 0))

        # Supplier Name
        col_sup = ctk.CTkFrame(sup_row, fg_color="transparent")
        col_sup.grid(row=0, column=1, padx=(6, 0), sticky="ew")
        lbl_s = ctk.CTkLabel(col_sup, text="Supplier / Vendor *", font=FONTS["small_bold"], text_color=THEME["text_body"])
        lbl_s.pack(anchor="w")
        self.entry_supplier = ctk.CTkEntry(col_sup, placeholder_text="e.g. Apex Industrial", height=34, font=FONTS["body"], border_color=THEME["card_border"])
        self.entry_supplier.pack(fill="x", pady=(2, 0))

        # Reason for modification (if edit)
        if self.is_edit:
            self._add_label("Reason for Change (Audit Requirement)")
            self.entry_reason = ctk.CTkEntry(
                self.body,
                placeholder_text="e.g. Updated supplier price quote",
                height=34,
                font=FONTS["body"],
                border_color=THEME["card_border"],
            )
            self.entry_reason.insert(0, "Inventory catalog information update")
            self.entry_reason.pack(fill="x", pady=(2, 10))

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

        btn_save = ctk.CTkButton(
            bottom_bar,
            text="Save Changes" if self.is_edit else "Create Product",
            font=FONTS["body_bold"],
            fg_color=THEME["primary"],
            hover_color=THEME["primary_hover"],
            height=36,
            command=self._handle_save,
        )
        btn_save.pack(side="right")

    def _add_label(self, text: str):
        lbl = ctk.CTkLabel(self.body, text=text, font=FONTS["small_bold"], text_color=THEME["text_body"])
        lbl.pack(anchor="w")

    def _on_sku_type(self, event):
        val = self.entry_sku.get()
        upper_val = val.upper()
        if val != upper_val:
            pos = self.entry_sku.index("insert")
            self.entry_sku.delete(0, "end")
            self.entry_sku.insert(0, upper_val)
            self.entry_sku.icursor(pos)

    def _populate_fields(self, product: Product):
        self.entry_name.insert(0, product.name)
        if product.category in ALLOWED_CATEGORIES:
            self.combo_category.set(product.category)
        self.entry_sku.insert(0, product.sku)
        self.entry_qty.delete(0, "end")
        self.entry_qty.insert(0, str(product.quantity))
        self.entry_price.insert(0, f"{product.unit_price:.2f}")
        self.entry_reorder.delete(0, "end")
        self.entry_reorder.insert(0, str(product.reorder_level))
        self.entry_supplier.insert(0, product.supplier_name)

    def _handle_save(self):
        # Hide previous error
        self.error_frame.pack_forget()

        data = {
            "name": self.entry_name.get(),
            "category": self.combo_category.get(),
            "sku": self.entry_sku.get(),
            "quantity": self.entry_qty.get(),
            "unit_price": self.entry_price.get(),
            "reorder_level": self.entry_reorder.get(),
            "supplier_name": self.entry_supplier.get(),
        }

        try:
            if self.is_edit:
                reason = self.entry_reason.get().strip() or "Standard catalog update"
                saved = product_service.update_product(self.product.product_id, data, change_reason=reason)
            else:
                saved = product_service.create_product(data, change_reason="Initial catalog registration")

            if self.on_save_success:
                self.on_save_success(saved)
            self.destroy()

        except ValidationError as e:
            self.lbl_error.configure(text=f"Validation Error: {e.message}")
            self.error_frame.pack(fill="x", pady=(0, 12), before=self.entry_pid)
        except Exception as ex:
            self.lbl_error.configure(text=f"System Error: {str(ex)}")
            self.error_frame.pack(fill="x", pady=(0, 12), before=self.entry_pid)


class ProductsView(ctk.CTkFrame):
    """Product Catalog management view with table, search, filters, and actions."""

    def __init__(self, master, on_data_change: Optional[Callable[[], None]] = None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self.on_data_change = on_data_change
        self.current_products: List[Product] = []

        self._build_ui()
        self.refresh()

    def _build_ui(self):
        # 1. Header Row
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 16))

        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left")

        lbl_title = ctk.CTkLabel(
            title_box,
            text="Product Catalog & Master Records",
            font=FONTS["h1"],
            text_color=THEME["text_dark"],
        )
        lbl_title.pack(anchor="w")

        lbl_sub = ctk.CTkLabel(
            title_box,
            text="Strict validation • Controlled categories • SKU format enforcement",
            font=FONTS["small"],
            text_color=THEME["text_muted"],
        )
        lbl_sub.pack(anchor="w")

        btn_new = ctk.CTkButton(
            header,
            text="+ Add New Product",
            font=FONTS["body_bold"],
            fg_color=THEME["primary"],
            hover_color=THEME["primary_hover"],
            height=36,
            command=self._open_add_dialog,
        )
        btn_new.pack(side="right")

        # 2. Controls Toolbar (Search with Auto-complete + Category Filter + Refresh)
        toolbar = ctk.CTkFrame(
            self,
            fg_color=THEME["card_bg"],
            corner_radius=THEME["card_radius"],
            border_width=THEME["border_width"],
            border_color=THEME["card_border"],
            height=54,
        )
        toolbar.pack(fill="x", pady=(0, 12))

        # Search Bar with Autocomplete (Q07 Feature 3)
        lbl_s = ctk.CTkLabel(toolbar, text="Search:", font=FONTS["small_bold"], text_color=THEME["text_muted"])
        lbl_s.pack(side="left", padx=(14, 6))

        self.search_entry = AutocompleteEntry(
            toolbar,
            product_service=product_service,
            placeholder_text="Search product name or SKU...",
            on_select=self._on_autocomplete_selected,
            width=280,
        )
        self.search_entry.pack(side="left", padx=(0, 12), pady=9)

        # Category Filter Dropdown (Q07 Feature 2)
        lbl_c = ctk.CTkLabel(toolbar, text="Category:", font=FONTS["small_bold"], text_color=THEME["text_muted"])
        lbl_c.pack(side="left", padx=(6, 6))

        category_options = ["All"] + ALLOWED_CATEGORIES
        self.combo_cat_filter = ctk.CTkOptionMenu(
            toolbar,
            values=category_options,
            font=FONTS["body"],
            fg_color=THEME["bg_main"],
            button_color=THEME["secondary"],
            button_hover_color=THEME["secondary_hover"],
            text_color=THEME["text_dark"],
            dropdown_text_color=THEME["text_dark"],
            dropdown_fg_color="#FFFFFF",
            width=150,
            command=lambda _: self.refresh(),
        )
        self.combo_cat_filter.set("All")
        self.combo_cat_filter.pack(side="left", padx=(0, 12), pady=9)

        # Clear / Reset button
        btn_reset = ctk.CTkButton(
            toolbar,
            text="Reset Filters",
            font=FONTS["small"],
            fg_color=THEME["bg_main"],
            text_color=THEME["text_body"],
            border_width=1,
            border_color=THEME["card_border"],
            hover_color=THEME["table_header_bg"],
            width=100,
            height=32,
            command=self._reset_filters,
        )
        btn_reset.pack(side="left", padx=(0, 8), pady=9)

        # Product count badge in toolbar
        self.lbl_count_badge = ctk.CTkLabel(
            toolbar,
            text="Showing: 0 items",
            font=FONTS["small_bold"],
            text_color=THEME["primary"],
        )
        self.lbl_count_badge.pack(side="right", padx=16)

        # 3. Products Table
        table_columns = [
            {"key": "product_id", "title": "ID", "width": 85, "align": "w"},
            {"key": "name", "title": "Product Name", "width": 200, "align": "w"},
            {"key": "category", "title": "Category", "width": 110, "align": "w"},
            {"key": "sku", "title": "SKU", "width": 120, "align": "w"},
            {"key": "quantity", "title": "Stock", "width": 60, "align": "center"},
            {"key": "unit_price", "title": "Unit Price", "width": 90, "align": "e"},
            {"key": "valuation", "title": "Valuation", "width": 100, "align": "e"},
            {"key": "supplier_name", "title": "Supplier", "width": 150, "align": "w"},
        ]

        self.table = TableView(
            self,
            columns=table_columns,
            on_select=self._on_table_row_click,
            empty_text="No products matching the search query or category filter.",
        )
        self.table.pack(fill="both", expand=True)

    def refresh(self):
        """Queries database with current search and category filters."""
        query = self.search_entry.get_text()
        cat_filter = self.combo_cat_filter.get()

        self.current_products = product_service.get_all_products(
            search_query=query,
            category_filter=cat_filter,
            sort_by="product_id",
            sort_ascending=True,
        )

        rows = []
        for p in self.current_products:
            rows.append({
                "product_id": p.product_id,
                "name": p.name,
                "category": p.category,
                "sku": p.sku,
                "quantity": p.quantity,
                "unit_price": f"${p.unit_price:.2f}",
                "valuation": f"${p.total_valuation:,.2f}",
                "supplier_name": p.supplier_name,
                "_raw": p,
            })

        action_buttons = [
            {"name": "view", "label": "👁️ Details", "color": THEME["secondary"], "width": 72},
            {"name": "edit", "label": "Edit", "color": THEME["primary"], "width": 48},
            {"name": "delete", "label": "Delete", "color": THEME["danger"], "width": 54},
        ]

        self.table.set_data(
            rows=rows,
            action_callback=self._handle_row_action,
            action_buttons=action_buttons,
        )

        self.lbl_count_badge.configure(text=f"Showing: {len(rows)} products")

    def _on_autocomplete_selected(self, item: Dict[str, str]):
        self.refresh()

    def _reset_filters(self):
        self.search_entry.set_text("")
        self.combo_cat_filter.set("All")
        self.refresh()

    def _open_add_dialog(self):
        ProductModalDialog(self, on_save_success=self._on_product_saved)

    def _open_product_details(self, product: Product):
        """Opens deep-link detail dialog with working edit controls."""
        ProductDetailDialog(self, product=product, on_data_change=self.refresh)

    def _on_table_row_click(self, row: Dict[str, Any]):
        """Callback when user clicks directly on a product row."""
        if "_raw" in row and isinstance(row["_raw"], Product):
            self._open_product_details(row["_raw"])

    def _handle_row_action(self, action: str, row: Dict[str, Any]):
        product: Product = row["_raw"]
        if action == "view":
            self._open_product_details(product)
        elif action == "edit":
            ProductModalDialog(self, product=product, on_save_success=self._on_product_saved)
        elif action == "delete":
            self._handle_delete_product(product)

    def _handle_delete_product(self, product: Product):
        # Q07 Feature 4: Confirmation Modal
        confirmed = ConfirmDialog.ask(
            self,
            title="Confirm Product Deletion",
            message=f"Are you sure you want to permanently delete product '{product.name}'? This action will archive historical records and write to the audit log.",
            details={
                "Product ID": product.product_id,
                "Name": product.name,
                "SKU": product.sku,
                "Current Stock": f"{product.quantity} units",
                "Total Valuation": f"${product.total_valuation:,.2f}",
            },
            confirm_text="Delete Product",
            is_destructive=True,
        )

        if not confirmed:
            return

        try:
            product_service.delete_product(product.product_id, reason="Operator confirmed manual deletion")
            self._on_product_saved(None)
        except Exception as e:
            ConfirmDialog.ask(
                self,
                title="Deletion Error",
                message=f"Failed to delete product: {str(e)}",
                confirm_text="OK",
                cancel_text="Close",
            )

    def _on_product_saved(self, saved_product: Optional[Product]):
        self.refresh()
        if self.on_data_change:
            self.on_data_change()
