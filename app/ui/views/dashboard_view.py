"""Dashboard View: Real-time inventory KPIs, Category Chart, and Recent Activity."""

from typing import Callable, Optional
import customtkinter as ctk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from app.services import inventory_service
from app.ui.components import StatCard
from app.ui.theme import THEME, FONTS


class DashboardView(ctk.CTkFrame):
    """Executive Dashboard with dynamic metrics, embedded Matplotlib charts, and quick actions."""

    def __init__(
        self,
        master,
        nav_callback: Optional[Callable[[str], None]] = None,
        **kwargs,
    ):
        super().__init__(master, fg_color="transparent", **kwargs)

        self.nav_callback = nav_callback
        self.canvas_widget = None

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
            text="Executive Inventory Dashboard",
            font=FONTS["h1"],
            text_color=THEME["text_dark"],
        )
        lbl_title.pack(anchor="w")

        lbl_sub = ctk.CTkLabel(
            title_box,
            text="Real-time SQLite relational metrics • TQM Q07 Data Accuracy Verification",
            font=FONTS["small"],
            text_color=THEME["text_muted"],
        )
        lbl_sub.pack(anchor="w")

        # Quick Actions in header
        btn_box = ctk.CTkFrame(header, fg_color="transparent")
        btn_box.pack(side="right")

        btn_add = ctk.CTkButton(
            btn_box,
            text="+ Add Product",
            font=FONTS["body_bold"],
            fg_color=THEME["primary"],
            hover_color=THEME["primary_hover"],
            height=36,
            command=lambda: self.nav_callback("products") if self.nav_callback else None,
        )
        btn_add.pack(side="left", padx=4)

        btn_refresh = ctk.CTkButton(
            btn_box,
            text="Refresh Data",
            font=FONTS["body"],
            fg_color=THEME["card_bg"],
            text_color=THEME["text_body"],
            border_width=1,
            border_color=THEME["card_border"],
            hover_color=THEME["table_header_bg"],
            height=36,
            command=self.refresh,
        )
        btn_refresh.pack(side="left", padx=4)

        # 2. Metric Stat Cards Row (4 cards)
        self.cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.cards_frame.pack(fill="x", pady=(0, 16))
        self.cards_frame.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="stat_cards")

        self.card_products = StatCard(
            self.cards_frame,
            title="Unique Products",
            value="--",
            subtitle="Catalog count",
            accent_color=THEME["primary"],
        )
        self.card_products.grid(row=0, column=0, padx=(0, 8), sticky="ew")

        self.card_units = StatCard(
            self.cards_frame,
            title="Units in Stock",
            value="--",
            subtitle="Verified count",
            accent_color=THEME["info"],
        )
        self.card_units.grid(row=0, column=1, padx=4, sticky="ew")

        self.card_val = StatCard(
            self.cards_frame,
            title="Total Valuation",
            value="--",
            subtitle="Sum(Qty × Price)",
            accent_color=THEME["success"],
        )
        self.card_val.grid(row=0, column=2, padx=4, sticky="ew")

        self.card_low = StatCard(
            self.cards_frame,
            title="Low Stock Alerts",
            value="--",
            subtitle="Qty <= Reorder Level",
            accent_color=THEME["danger"],
        )
        self.card_low.grid(row=0, column=3, padx=(8, 0), sticky="ew")

        # 3. Middle Section: Category Chart (Left) + Recent Activity Feed (Right)
        self.mid_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.mid_frame.pack(fill="both", expand=True)
        self.mid_frame.grid_columnconfigure(0, weight=3)
        self.mid_frame.grid_columnconfigure(1, weight=2)
        self.mid_frame.grid_rowconfigure(0, weight=1)

        # Left: Matplotlib Category Distribution Card
        self.chart_card = ctk.CTkFrame(
            self.mid_frame,
            fg_color=THEME["card_bg"],
            corner_radius=THEME["card_radius"],
            border_width=THEME["border_width"],
            border_color=THEME["card_border"],
        )
        self.chart_card.grid(row=0, column=0, padx=(0, 8), sticky="nsew")

        chart_title = ctk.CTkLabel(
            self.chart_card,
            text="CATEGORY VALUATION BREAKDOWN",
            font=FONTS["h3"],
            text_color=THEME["text_muted"],
            anchor="w",
        )
        chart_title.pack(fill="x", padx=16, pady=(12, 4))

        self.chart_container = ctk.CTkFrame(self.chart_card, fg_color="transparent")
        self.chart_container.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        # Right: Recent Activity Card
        self.activity_card = ctk.CTkFrame(
            self.mid_frame,
            fg_color=THEME["card_bg"],
            corner_radius=THEME["card_radius"],
            border_width=THEME["border_width"],
            border_color=THEME["card_border"],
        )
        self.activity_card.grid(row=0, column=1, padx=(8, 0), sticky="nsew")

        act_title = ctk.CTkLabel(
            self.activity_card,
            text="RECENT AUDIT ACTIVITIES",
            font=FONTS["h3"],
            text_color=THEME["text_muted"],
            anchor="w",
        )
        act_title.pack(fill="x", padx=16, pady=(12, 8))

        self.activity_scroll = ctk.CTkScrollableFrame(self.activity_card, fg_color="transparent")
        self.activity_scroll.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        self._anim_timer = None

    def refresh(self):
        """Fetches live summary data and redraws metrics, chart, and activity."""
        summary = inventory_service.get_inventory_summary()

        # Update cards
        self.card_products.update_values(str(summary["total_products"]))
        self.card_units.update_values(f"{summary['total_units']:,}")
        self.card_val.update_values(f"${summary['total_valuation']:,.2f}")
        self.card_low.update_values(str(summary["low_stock_count"]))

        # Redraw Animated & Interactive Matplotlib Bar Chart
        self._render_chart(summary["category_breakdown"], total_valuation=summary["total_valuation"])

        # Render Activity
        self._render_activity(summary["recent_activities"])

    def _render_chart(self, category_data, total_valuation=0.0):
        # Cancel any pending animation
        if hasattr(self, "_anim_timer") and self._anim_timer:
            try:
                self.after_cancel(self._anim_timer)
            except Exception:
                pass
            self._anim_timer = None

        if self.canvas_widget:
            self.canvas_widget.destroy()

        fig = Figure(figsize=(5.2, 3.3), dpi=100)
        fig.patch.set_facecolor("#FFFFFF")
        ax = fig.add_subplot(111)
        ax.set_facecolor("#FFFFFF")

        if category_data:
            categories = [c["category"] for c in category_data]
            target_valuations = [float(c["valuation"]) for c in category_data]
            base_palette = ["#2563EB", "#0284C7", "#16A34A", "#D97706", "#9333EA", "#0D9488"]
            bar_colors = [base_palette[i % len(base_palette)] for i in range(len(categories))]

            # Start bars at 0 for smooth growth animation
            bars = ax.bar(
                categories,
                [0.0] * len(categories),
                color=bar_colors,
                width=0.55,
                edgecolor="none",
                zorder=3,
            )

            ax.set_ylabel("Valuation ($)", fontsize=9, color="#64748B", fontweight="bold")
            ax.set_title("[Interactive] Hover over bars to view live breakdown", fontsize=8, color="#0284C7", pad=6)
            ax.tick_params(axis="x", labelrotation=20, labelsize=8, colors="#334155")
            ax.tick_params(axis="y", labelsize=8, colors="#334155")
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.spines["left"].set_color("#E2E8F0")
            ax.spines["bottom"].set_color("#E2E8F0")
            ax.grid(axis="y", linestyle="--", alpha=0.35, color="#CBD5E1", zorder=1)

            max_val = max(target_valuations) if target_valuations else 1000.0
            ax.set_ylim(0, max_val * 1.30)

            # Value labels above bars
            value_texts = []
            for i, cat in enumerate(categories):
                txt = ax.text(
                    i,
                    0,
                    "",
                    ha="center",
                    va="bottom",
                    fontsize=7.5,
                    color="#0F172A",
                    fontweight="bold",
                    zorder=4,
                )
                value_texts.append(txt)

            # Interactive Hover Annotation Tooltip Box
            annot = ax.annotate(
                "",
                xy=(0, 0),
                xytext=(0, 18),
                textcoords="offset points",
                bbox=dict(
                    boxstyle="round,pad=0.65,rounding_size=0.35",
                    fc="#0F172A",
                    ec="#38BDF8",
                    lw=1.6,
                    alpha=0.96,
                ),
                color="#FFFFFF",
                fontsize=8.5,
                ha="center",
                va="bottom",
                zorder=10,
            )
            annot.set_visible(False)

            # Tooltip information strings
            tooltips = []
            for c in category_data:
                v = float(c["valuation"])
                u = int(c.get("units", 0))
                cnt = int(c.get("product_count", 0))
                pct = (v / total_valuation * 100) if total_valuation > 0 else 0.0
                t_str = f"Category: {c['category']}\nValuation: ${v:,.2f} ({pct:.1f}%)\nStock: {u:,} units | {cnt} items"
                tooltips.append(t_str)

            # Hover event handler
            def on_hover(event):
                if event.inaxes != ax:
                    if annot.get_visible():
                        annot.set_visible(False)
                        for b, orig_c in zip(bars, bar_colors):
                            b.set_facecolor(orig_c)
                            b.set_edgecolor("none")
                            b.set_alpha(1.0)
                        canvas.draw_idle()
                    return

                hovered_idx = -1
                for idx, b in enumerate(bars):
                    contains, _ = b.contains(event)
                    if contains:
                        hovered_idx = idx
                        break

                if hovered_idx != -1:
                    # Highlight hovered bar and dim others
                    for idx, (b, orig_c) in enumerate(zip(bars, bar_colors)):
                        if idx == hovered_idx:
                            b.set_facecolor(orig_c)
                            b.set_edgecolor("#0F172A")
                            b.set_linewidth(1.8)
                            b.set_alpha(1.0)
                        else:
                            b.set_facecolor(orig_c)
                            b.set_edgecolor("none")
                            b.set_alpha(0.35)

                    target_bar = bars[hovered_idx]
                    x_center = target_bar.get_x() + target_bar.get_width() / 2
                    y_top = target_bar.get_height()
                    annot.xy = (x_center, y_top)
                    annot.set_text(tooltips[hovered_idx])
                    annot.set_visible(True)
                    canvas.draw_idle()
                else:
                    if annot.get_visible():
                        annot.set_visible(False)
                        for b, orig_c in zip(bars, bar_colors):
                            b.set_facecolor(orig_c)
                            b.set_edgecolor("none")
                            b.set_alpha(1.0)
                        canvas.draw_idle()

        else:
            ax.text(0.5, 0.5, "No Category Data Available", ha="center", va="center", color="#94A3B8")
            ax.axis("off")

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
        canvas.draw()
        self.canvas_widget = canvas.get_tk_widget()
        self.canvas_widget.pack(fill="both", expand=True)

        if category_data:
            canvas.mpl_connect("motion_notify_event", on_hover)

            # Smooth opening animation: 18 frames over ~270ms with cubic ease-out
            total_frames = 18
            def animate_step(frame=1):
                if not self.winfo_exists() or not self.chart_container.winfo_exists():
                    return
                t = frame / total_frames
                ease = 1.0 - (1.0 - t) ** 3  # cubic ease-out

                for b, target_h, txt in zip(bars, target_valuations, value_texts):
                    cur_h = target_h * ease
                    b.set_height(cur_h)
                    txt.set_position((b.get_x() + b.get_width() / 2, cur_h + max_val * 0.015))
                    txt.set_text(f"${cur_h:,.0f}")

                canvas.draw_idle()

                if frame < total_frames:
                    self._anim_timer = self.after(15, lambda: animate_step(frame + 1))
                else:
                    for b, target_h, txt in zip(bars, target_valuations, value_texts):
                        b.set_height(target_h)
                        txt.set_position((b.get_x() + b.get_width() / 2, target_h + max_val * 0.015))
                        txt.set_text(f"${target_h:,.0f}")
                    canvas.draw_idle()
                    self._anim_timer = None

            self._anim_timer = self.after(40, animate_step)

    def _render_activity(self, activities):
        for child in self.activity_scroll.winfo_children():
            child.destroy()

        if not activities:
            lbl = ctk.CTkLabel(
                self.activity_scroll,
                text="No audit events recorded yet.",
                font=FONTS["small"],
                text_color=THEME["text_muted"],
            )
            lbl.pack(pady=20)
            return

        for act in activities:
            item_box = ctk.CTkFrame(
                self.activity_scroll,
                fg_color=THEME["bg_main"],
                corner_radius=6,
                border_width=1,
                border_color=THEME["card_border"],
            )
            item_box.pack(fill="x", pady=3)

            top = ctk.CTkFrame(item_box, fg_color="transparent")
            top.pack(fill="x", padx=10, pady=(6, 2))

            # Action badge
            action_name = act["action"]
            badge_color = THEME["primary"]
            if action_name == "CREATE":
                badge_color = THEME["success"]
            elif action_name == "DELETE":
                badge_color = THEME["danger"]
            elif action_name == "STOCK_ADJUSTMENT":
                badge_color = THEME["warning"]

            lbl_badge = ctk.CTkLabel(
                top,
                text=action_name,
                font=FONTS["small_bold"],
                text_color=badge_color,
            )
            lbl_badge.pack(side="left")

            lbl_time = ctk.CTkLabel(
                top,
                text=act["timestamp"].split()[0],
                font=FONTS["small"],
                text_color=THEME["text_muted"],
            )
            lbl_time.pack(side="right")

            lbl_desc = ctk.CTkLabel(
                item_box,
                text=f"{act['entity_id']} • {act.get('reason') or 'No reason provided'}",
                font=FONTS["small"],
                text_color=THEME["text_dark"],
                anchor="w",
            )
            lbl_desc.pack(fill="x", padx=10, pady=(0, 6))
