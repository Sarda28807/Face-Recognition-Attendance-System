"""
Design System — Premium Dark Navy/Purple Theme
================================================

Centralized visual constants for the Face Attendance System.
Inspired by modern SaaS analytics dashboards with a dark,
futuristic aesthetic and purple/indigo brand identity.

All GUI files import from here to ensure visual consistency.
"""

# ============================================================
# COLOR PALETTE
# ============================================================

COLORS = {
    # Backgrounds (darkest → lightest)
    "bg":               "#0B1020",
    "surface":          "#10182B",
    "elevated":         "#142039",
    "card":             "#17233A",
    "card_hover":       "#1C2942",

    # Brand / Accents
    "purple":           "#8B5CF6",
    "purple_dark":      "#6D5AE6",
    "purple_muted":     "#7C3AED",
    "purple_glow":      "#8B5CF615",   # for subtle glows (low alpha hex)
    "blue":             "#3B82F6",
    "cyan":             "#22D3EE",

    # Semantic
    "success":          "#22C55E",
    "warning":          "#F59E0B",
    "danger":           "#EF4444",

    # Text
    "text":             "#F8FAFC",
    "text_secondary":   "#94A3B8",
    "muted":            "#64748B",

    # Borders
    "border":           "#263554",
    "border_light":     "#2D3F5E",

    # Sidebar
    "sidebar_bg":       "#0D1425",
    "sidebar_active":   "#8B5CF6",
    "sidebar_hover":    "#1A2340",

    # Inputs
    "input_bg":         "#0F1A2E",
    "input_border":     "#263554",
    "input_focus":      "#8B5CF6",

    # Table
    "table_header":     "#1A2744",
    "table_row_even":   "#131D33",
    "table_row_odd":    "#10182B",
    "table_row_hover":  "#1C2942",
}

# ============================================================
# TYPOGRAPHY
# ============================================================

# Primary font — Segoe UI is guaranteed on Windows and looks clean.
# If Inter is installed on the system it can be substituted.
FONT_FAMILY = "Segoe UI"

FONT_SIZES = {
    "page_title":    22,
    "section":       15,
    "card_number":   28,
    "card_number_lg": 36,
    "heading":       14,
    "body":          13,
    "small":         11,
    "tiny":          10,
    "nav":           13,
}

# ============================================================
# SPACING
# ============================================================

PAD = {
    "xs":  4,
    "sm":  8,
    "md":  12,
    "lg":  16,
    "xl":  20,
    "xxl": 28,
    "page": 24,     # outer page padding
}

# ============================================================
# BORDER RADIUS
# ============================================================

RADIUS = {
    "sm":  8,
    "md":  12,
    "lg":  16,
    "xl":  20,
}

# ============================================================
# SIDEBAR
# ============================================================

SIDEBAR_WIDTH = 210

NAV_ITEMS = [
    ("\u25C6", "Dashboard",    "dashboard"),    # ◆
    ("\u25CE", "Register",     "registration"),  # ◎
    ("\u25C9", "Recognition",  "recognition"),   # ◉
    ("\u2630", "Attendance",   "attendance"),     # ☰
    ("\u25C8", "Analytics",    "statistics"),     # ◈
    ("\u2699", "Settings",     "settings"),       # ⚙
]

# ============================================================
# MATPLOTLIB CHART STYLING
# ============================================================

CHART = {
    "bg":           "#17233A",
    "axes_bg":      "#17233A",
    "grid_color":   "#263554",
    "grid_alpha":   0.3,
    "text_color":   "#94A3B8",
    "title_color":  "#F8FAFC",
    "line_color":   "#8B5CF6",
    "fill_color":   "#8B5CF6",
    "fill_alpha":   0.2,
    "spine_color":  "#263554",
    "tick_color":   "#64748B",
    "dpi":          100,
}
