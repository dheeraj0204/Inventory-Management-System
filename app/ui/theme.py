"""Enterprise UI Theme and Design Tokens for CustomTkinter."""

# Color Palette - Modern Enterprise Theme
THEME = {
    # Sidebar
    "sidebar_bg": "#0F172A",          # Slate 900
    "sidebar_hover": "#1E293B",       # Slate 800
    "sidebar_active": "#2563EB",      # Blue 600
    "sidebar_text": "#F8FAFC",        # Slate 50
    "sidebar_text_muted": "#94A3B8",  # Slate 400
    "sidebar_border": "#334155",      # Slate 700

    # Canvas & Backgrounds
    "bg_main": "#F8FAFC",             # Slate 50
    "card_bg": "#FFFFFF",             # White
    "card_border": "#E2E8F0",         # Slate 200
    "header_bg": "#FFFFFF",

    # Brand & Action Colors
    "primary": "#2563EB",             # Blue 600
    "primary_hover": "#1D4ED8",       # Blue 700
    "primary_light": "#EFF6FF",       # Blue 50
    "secondary": "#64748B",           # Slate 500
    "secondary_hover": "#475569",     # Slate 600

    # Status Colors (TQM / Data Integrity)
    "success": "#16A34A",             # Green 600
    "success_hover": "#15803D",       # Green 700
    "success_bg": "#DCFCE7",          # Green 100
    "warning": "#D97706",             # Amber 600
    "warning_hover": "#B45309",       # Amber 700
    "warning_bg": "#FEF3C7",          # Amber 100
    "danger": "#DC2626",              # Red 600
    "danger_hover": "#B91C1C",        # Red 700
    "danger_bg": "#FEE2E2",           # Red 100
    "info": "#0284C7",                # Sky 600
    "info_hover": "#0369A1",          # Sky 700
    "info_bg": "#E0F2FE",             # Sky 100

    # Typography Colors
    "text_dark": "#0F172A",           # Slate 900
    "text_body": "#334155",           # Slate 700
    "text_muted": "#64748B",          # Slate 500
    "text_light": "#FFFFFF",

    # Table styling
    "table_header_bg": "#F1F5F9",
    "table_row_alt": "#F8FAFC",
    "table_row_selected": "#E0E7FF",
    "table_border": "#CBD5E1",

    # Dimensions & Radii
    "corner_radius": 8,
    "card_radius": 10,
    "button_radius": 6,
    "border_width": 1,
}

# Typography font families
FONTS = {
    "h1": ("Segoe UI", 20, "bold"),
    "h2": ("Segoe UI", 16, "bold"),
    "h3": ("Segoe UI", 13, "bold"),
    "body": ("Segoe UI", 11),
    "body_bold": ("Segoe UI", 11, "bold"),
    "small": ("Segoe UI", 9),
    "small_bold": ("Segoe UI", 9, "bold"),
    "metric": ("Segoe UI", 24, "bold"),
    "code": ("Consolas", 10),
}
