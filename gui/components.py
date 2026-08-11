"""
Reusable UI Components — Premium Theme
=======================================

Provides styled widget classes that enforce the design system.
Import these instead of creating raw CTkFrame/CTkLabel widgets.
"""

import customtkinter as ctk
from gui.theme import COLORS, FONT_FAMILY, FONT_SIZES, RADIUS, PAD


# ============================================================
# Helpers
# ============================================================

def font(size_key_or_int, weight="normal"):
    """Create a CTkFont using the design system."""
    if isinstance(size_key_or_int, str):
        size = FONT_SIZES.get(size_key_or_int, 13)
    else:
        size = size_key_or_int
    return ctk.CTkFont(family=FONT_FAMILY, size=size, weight=weight)


def darken(hex_color: str, factor: float = 0.75) -> str:
    """Darken a hex colour for hover/pressed states."""
    try:
        h = hex_color.lstrip("#")
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return f"#{int(r*factor):02x}{int(g*factor):02x}{int(b*factor):02x}"
    except (ValueError, IndexError):
        return hex_color


# ============================================================
# ModernCard
# ============================================================

class ModernCard(ctk.CTkFrame):
    """Base rounded card with dark surface and subtle border."""

    def __init__(self, parent, **kw):
        defaults = dict(
            fg_color=COLORS["card"],
            corner_radius=RADIUS["lg"],
            border_width=1,
            border_color=COLORS["border"],
        )
        defaults.update(kw)
        super().__init__(parent, **defaults)


# ============================================================
# StatCard
# ============================================================

class StatCard(ModernCard):
    """Compact stat card: icon · label · large number · subtitle."""

    def __init__(self, parent, *, icon: str, label: str,
                 value="0", subtitle="", accent=COLORS["purple"], **kw):
        super().__init__(parent, **kw)

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=14, pady=(14, 0))

        ctk.CTkLabel(top, text=icon, font=font(18),
                     text_color=accent).pack(side="left")
        ctk.CTkLabel(top, text=label, font=font("small"),
                     text_color=COLORS["text_secondary"]).pack(side="left", padx=(8, 0))

        self.value_label = ctk.CTkLabel(
            self, text=str(value), font=font("card_number", "bold"),
            text_color=COLORS["text"],
        )
        self.value_label.pack(padx=14, pady=(2, 0), anchor="w")

        if subtitle:
            ctk.CTkLabel(
                self, text=subtitle, font=font("tiny"),
                text_color=COLORS["muted"],
            ).pack(padx=14, pady=(0, 12), anchor="w")
        else:
            ctk.CTkLabel(self, text="", height=6).pack()  # spacer

    def set_value(self, value):
        self.value_label.configure(text=str(value))


# ============================================================
# ActionCard
# ============================================================

class ActionCard(ModernCard):
    """Compact clickable action card with hover glow."""

    def __init__(self, parent, *, icon: str, title: str,
                 subtitle: str = "", command=None, accent=COLORS["purple"], **kw):
        super().__init__(parent, **kw)
        self._command = command
        self._default_border = COLORS["border"]
        self._accent = accent

        ctk.CTkLabel(self, text=icon, font=font(22),
                     text_color=accent).pack(padx=14, pady=(14, 4), anchor="w")

        ctk.CTkLabel(self, text=title, font=font("heading", "bold"),
                     text_color=COLORS["text"]).pack(padx=14, anchor="w")

        if subtitle:
            ctk.CTkLabel(self, text=subtitle, font=font("tiny"),
                         text_color=COLORS["muted"],
                         wraplength=160).pack(padx=14, pady=(2, 12), anchor="w")
        else:
            ctk.CTkLabel(self, text="", height=8).pack()

        # Bind click + hover
        self._bind_recursive(self)

    def _bind_recursive(self, widget):
        widget.bind("<Enter>", self._on_enter)
        widget.bind("<Leave>", self._on_leave)
        widget.bind("<Button-1>", self._on_click)
        for child in widget.winfo_children():
            self._bind_recursive(child)

    def _on_enter(self, _):
        self.configure(border_color=self._accent)

    def _on_leave(self, _):
        self.configure(border_color=self._default_border)

    def _on_click(self, _):
        if self._command:
            self._command()


# ============================================================
# SectionHeader
# ============================================================

class SectionHeader(ctk.CTkFrame):
    """Compact page/section header with title + subtitle + right widget."""

    def __init__(self, parent, title: str, subtitle: str = "",
                 right_text: str = "", **kw):
        kw.setdefault("fg_color", "transparent")
        super().__init__(parent, **kw)
        self.grid_columnconfigure(0, weight=1)

        left = ctk.CTkFrame(self, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(left, text=title, font=font("page_title", "bold"),
                     text_color=COLORS["text"]).pack(anchor="w")
        if subtitle:
            ctk.CTkLabel(left, text=subtitle, font=font("small"),
                         text_color=COLORS["muted"]).pack(anchor="w")

        if right_text:
            ctk.CTkLabel(self, text=right_text, font=font("small"),
                         text_color=COLORS["text_secondary"]
                         ).grid(row=0, column=1, sticky="e")


# ============================================================
# StatusBadge
# ============================================================

class StatusBadge(ctk.CTkFrame):
    """Tiny coloured dot + label."""

    def __init__(self, parent, text: str, color: str = COLORS["success"], **kw):
        kw.setdefault("fg_color", "transparent")
        super().__init__(parent, **kw)
        ctk.CTkLabel(self, text="●", font=font(10),
                     text_color=color).pack(side="left")
        self.label = ctk.CTkLabel(self, text=text, font=font("small"),
                                  text_color=COLORS["text_secondary"])
        self.label.pack(side="left", padx=(4, 0))

    def set(self, text: str, color: str):
        for w in self.winfo_children():
            if w.cget("text") == "●":
                w.configure(text_color=color)
        self.label.configure(text=text)


# ============================================================
# ModernButton
# ============================================================

class ModernButton(ctk.CTkButton):
    """Styled button matching the premium theme."""

    def __init__(self, parent, text: str, accent=COLORS["purple"], **kw):
        defaults = dict(
            text=text,
            font=font("body", "bold"),
            height=36,
            corner_radius=RADIUS["sm"],
            fg_color=accent,
            hover_color=darken(accent),
            text_color=COLORS["text"],
        )
        defaults.update(kw)
        super().__init__(parent, **defaults)


# ============================================================
# ModernEntry
# ============================================================

class ModernEntry(ctk.CTkEntry):
    """Styled text input matching the premium theme."""

    def __init__(self, parent, **kw):
        defaults = dict(
            height=36,
            corner_radius=RADIUS["sm"],
            font=font("body"),
            fg_color=COLORS["input_bg"],
            border_color=COLORS["input_border"],
            text_color=COLORS["text"],
            placeholder_text_color=COLORS["muted"],
        )
        defaults.update(kw)
        super().__init__(parent, **defaults)


# ============================================================
# Toast Notification
# ============================================================

class Toast(ctk.CTkFrame):
    """Floating notification that auto-dismisses.

    Usage (from any page with access to self.app):
        Toast.show(self.app, "Attendance marked!", "success")
    """

    @staticmethod
    def show(root, message: str, kind: str = "info", duration: int = 3000):
        """
        Show a toast notification.

        Parameters:
            root:     the CTk root window.
            message:  notification text.
            kind:     'success' | 'warning' | 'danger' | 'info'
            duration: auto-dismiss milliseconds.
        """
        accent = {
            "success": COLORS["success"],
            "warning": COLORS["warning"],
            "danger":  COLORS["danger"],
            "info":    COLORS["purple"],
        }.get(kind, COLORS["purple"])

        icon = {"success": "✓", "warning": "⚠", "danger": "✕", "info": "ℹ"}.get(kind, "ℹ")

        toast = ctk.CTkFrame(
            root, fg_color=COLORS["elevated"],
            corner_radius=RADIUS["md"],
            border_width=1, border_color=accent,
            height=44,
        )
        toast.place(relx=1.0, rely=0.0, anchor="ne", x=-20, y=20)
        toast.lift()

        inner = ctk.CTkFrame(toast, fg_color="transparent")
        inner.pack(padx=14, pady=10, fill="x")

        ctk.CTkLabel(inner, text=icon, font=font(14, "bold"),
                     text_color=accent).pack(side="left")
        ctk.CTkLabel(inner, text=message, font=font("small"),
                     text_color=COLORS["text"]).pack(side="left", padx=(8, 0))

        def _dismiss():
            try:
                toast.destroy()
            except Exception:
                pass

        root.after(duration, _dismiss)
