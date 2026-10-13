"""Debounced auto-complete entry widget (Q07 Feature 3: Search with Auto-complete)."""

from typing import Callable, Dict, List, Optional
import customtkinter as ctk
from app.services.product_service import ProductService
from app.ui.theme import THEME, FONTS


class AutocompleteEntry(ctk.CTkFrame):
    """Entry widget with debounced popover search suggestions querying real SQLite records."""

    def __init__(
        self,
        master,
        product_service: ProductService,
        placeholder_text: str = "Search by name or SKU...",
        on_select: Optional[Callable[[Dict[str, str]], None]] = None,
        width: int = 300,
        **kwargs,
    ):
        super().__init__(master, fg_color="transparent", **kwargs)

        self.product_service = product_service
        self.on_select = on_select
        self._debounce_timer: Optional[str] = None
        self._popup: Optional[ctk.CTkToplevel] = None

        # Container layout
        self.entry = ctk.CTkEntry(
            self,
            placeholder_text=placeholder_text,
            width=width,
            height=36,
            font=FONTS["body"],
            corner_radius=THEME["button_radius"],
            border_width=THEME["border_width"],
            border_color=THEME["card_border"],
            fg_color=THEME["card_bg"],
            text_color=THEME["text_dark"],
        )
        self.entry.pack(fill="x", expand=True)

        # Bind typing and focus events
        self.entry.bind("<KeyRelease>", self._on_key_release)
        self.entry.bind("<FocusOut>", self._on_focus_out)
        self.entry.bind("<Return>", self._on_enter)

    def get_text(self) -> str:
        return self.entry.get().strip()

    def set_text(self, text: str) -> None:
        self.entry.delete(0, "end")
        self.entry.insert(0, text)

    def _on_key_release(self, event):
        # Ignore navigation keys
        if event.keysym in ("Up", "Down", "Return", "Escape", "Tab"):
            return

        # Cancel previous debounce timer
        if self._debounce_timer:
            self.after_cancel(self._debounce_timer)

        # Debounce query by 180ms
        self._debounce_timer = self.after(180, self._perform_search)

    def _perform_search(self):
        query = self.get_text()
        if len(query) < 2:
            self._close_popup()
            return

        try:
            results = self.product_service.search_autocomplete(query, limit=6)
            if results:
                self._show_suggestions(results)
            else:
                self._close_popup()
        except Exception:
            self._close_popup()

    def _show_suggestions(self, items: List[Dict[str, str]]):
        if not self._popup:
            self._popup = ctk.CTkToplevel(self)
            self._popup.overrideredirect(True)
            self._popup.configure(fg_color=THEME["card_bg"])

        # Position popup directly under the entry widget
        self.update_idletasks()
        try:
            x = self.entry.winfo_rootx()
            y = self.entry.winfo_rooty() + self.entry.winfo_height() + 2
            w = max(self.entry.winfo_width(), 320)
            self._popup.geometry(f"{w}x{len(items) * 40 + 8}+{x}+{y}")
        except Exception:
            pass

        # Clear existing items
        for child in self._popup.winfo_children():
            child.destroy()

        # Build suggestions list
        container = ctk.CTkFrame(
            self._popup,
            fg_color=THEME["card_bg"],
            corner_radius=6,
            border_width=1,
            border_color=THEME["primary"],
        )
        container.pack(fill="both", expand=True)

        for item in items:
            btn = ctk.CTkButton(
                container,
                text=item["display"],
                font=FONTS["small"],
                text_color=THEME["text_dark"],
                fg_color="transparent",
                hover_color=THEME["primary_light"],
                anchor="w",
                height=36,
                corner_radius=4,
                command=lambda it=item: self._select_item(it),
            )
            btn.pack(fill="x", padx=4, pady=2)

    def _select_item(self, item: Dict[str, str]):
        self.set_text(item["name"])
        self._close_popup()
        if self.on_select:
            self.on_select(item)

    def _on_enter(self, event):
        self._close_popup()
        if self.on_select:
            query = self.get_text()
            if query:
                self.on_select({"name": query, "sku": query, "product_id": ""})

    def _on_focus_out(self, event):
        # Delay closing so click inside popup registers
        self.after(250, self._close_popup)

    def _close_popup(self):
        if self._popup:
            try:
                self._popup.destroy()
            except Exception:
                pass
            self._popup = None
